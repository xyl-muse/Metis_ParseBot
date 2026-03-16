"""预审智能体"""
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.base import BaseAgent
from src.agents.reviewer.scorer import Scorer, ScoreResult
from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import ReviewError
from src.db.crud import CRUD
from src.db.models import Content

logger = get_logger(__name__)


class ReviewerAgent(BaseAgent):
    """
    预审智能体
    
    负责对采集的内容进行价值评分和筛选。
    """

    def __init__(self, **kwargs):
        super().__init__(name="ReviewerAgent", **kwargs)
        self.scorer = Scorer(self.llm)
        self.passing_score = settings.passing_score

    async def run(
        self,
        content_id: Optional[str] = None,
        session: Optional[AsyncSession] = None,
        limit: int = 50,
    ) -> dict:
        """
        执行预审任务

        Args:
            content_id: 指定内容ID，为空则处理所有待预审内容
            session: 数据库会话
            limit: 最大处理数量

        Returns:
            预审结果统计
        """
        if not session:
            raise ReviewError("需要数据库会话")

        results = {
            "total_processed": 0,
            "passed": 0,
            "rejected": 0,
            "errors": [],
        }

        # 获取待预审内容
        if content_id:
            contents = [await CRUD.get_content(session, content_id)]
            contents = [c for c in contents if c is not None]
        else:
            contents = await CRUD.list_contents(session, status="pending", limit=limit)

        logger.info(f"[{self.name}] 开始预审 {len(contents)} 条内容")

        for content in contents:
            try:
                score_result = await self._review_content(content, session)
                results["total_processed"] += 1

                if score_result.passed:
                    results["passed"] += 1
                else:
                    results["rejected"] += 1

            except Exception as e:
                logger.error(f"[{self.name}] 预审失败: {content.title[:50]}, 错误: {e}")
                results["errors"].append(str(e))

        logger.info(
            f"[{self.name}] 预审完成: 处理 {results['total_processed']}, "
            f"通过 {results['passed']}, 拒绝 {results['rejected']}"
        )

        return results

    async def _review_content(
        self,
        content: Content,
        session: AsyncSession,
    ) -> ScoreResult:
        """
        预审单个内容

        Args:
            content: 待预审内容
            session: 数据库会话

        Returns:
            评分结果
        """
        # 执行评分
        score_result = await self.scorer.score(
            title=content.title,
            source=content.source,
            category=content.category,
            summary=content.summary or content.raw_content or content.title,
        )

        # 获取拒绝原因（如果未通过）
        review_notes = score_result.brief_reason
        if not score_result.passed:
            review_notes = await self.scorer.get_rejection_reason(content.title, score_result)

        # 保存预审记录
        await CRUD.create_review(
            session=session,
            content_id=content.id,
            novelty_score=score_result.novelty_score,
            utility_score=score_result.utility_score,
            authority_score=score_result.authority_score,
            timeliness_score=score_result.timeliness_score,
            completeness_score=score_result.completeness_score,
            total_score=score_result.total_score,
            passed=score_result.passed,
            review_notes=review_notes,
        )

        # 更新内容状态
        new_status = "reviewed" if score_result.passed else "rejected"
        await CRUD.update_content_status(session, content.id, new_status)

        logger.debug(
            f"[{self.name}] 预审完成: {content.title[:30]}, "
            f"总分 {score_result.total_score}, {'通过' if score_result.passed else '拒绝'}"
        )

        return score_result

    async def review_single(
        self,
        title: str,
        source: str,
        category: str,
        summary: str,
    ) -> ScoreResult:
        """
        预审单个内容（不入库，用于测试）

        Args:
            title: 标题
            source: 来源
            category: 分类
            summary: 摘要

        Returns:
            评分结果
        """
        return await self.scorer.score(
            title=title,
            source=source,
            category=category,
            summary=summary,
        )

    async def get_pending_contents(
        self,
        session: AsyncSession,
        limit: int = 50,
    ) -> list[Content]:
        """
        获取待预审内容列表

        Args:
            session: 数据库会话
            limit: 最大数量

        Returns:
            待预审内容列表
        """
        return await CRUD.list_contents(session, status="pending", limit=limit)

    async def get_passed_contents(
        self,
        session: AsyncSession,
        limit: int = 50,
    ) -> list[Content]:
        """
        获取通过预审的内容列表（按分数降序）

        Args:
            session: 数据库会话
            limit: 最大数量

        Returns:
            通过预审的内容列表
        """
        reviews = await CRUD.list_passed_reviews(session, limit=limit)
        contents = []
        for review in reviews:
            content = await CRUD.get_content(session, review.content_id)
            if content and content.status == "reviewed":
                contents.append(content)
        return contents
