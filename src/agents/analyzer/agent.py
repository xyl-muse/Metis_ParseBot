"""总结分析智能体"""
import asyncio
import json
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.base import BaseAgent
from src.agents.analyzer.summarizer import Summarizer, SummaryResult
from src.agents.analyzer.knowledge import KnowledgeAnalyzer, KnowledgeAnalysisResult
from src.agents.analyzer.prompts import ANALYSIS_PROMPT, CROSS_DOMAIN_PROMPT
from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import AnalysisError
from src.db.crud import CRUD
from src.db.models import Content, Review

logger = get_logger(__name__)

# API 请求间隔（秒），防止 429 限流
API_REQUEST_DELAY = 3.0


class AnalyzerAgent(BaseAgent):
    """
    总结分析智能体
    
    负责对通过预审的内容进行深度分析和总结。
    """

    def __init__(self, progress_dict: Optional[dict] = None, **kwargs):
        super().__init__(name="AnalyzerAgent", **kwargs)
        self.summarizer = Summarizer(self.llm)
        self.knowledge_analyzer = KnowledgeAnalyzer(self.llm)
        # 进度追踪 - 支持外部传入或内部创建
        self._progress = progress_dict if progress_dict is not None else {
            "total": 0,
            "processed": 0,
            "success": 0,
            "failed": 0,
            "current_item": None,
            "status": "idle",
        }

    def get_progress(self) -> dict:
        """获取当前处理进度"""
        return self._progress.copy()

    def _update_progress(self, **kwargs):
        """更新进度"""
        for key, value in kwargs.items():
            if key in self._progress:
                self._progress[key] = value

    async def run(
        self,
        content_id: Optional[str] = None,
        session: Optional[AsyncSession] = None,
        limit: int = 50,
    ) -> dict:
        """
        执行分析任务

        Args:
            content_id: 指定内容ID，为空则处理所有待分析内容
            session: 数据库会话
            limit: 最大处理数量

        Returns:
            分析结果统计
        """
        if not session:
            raise AnalysisError("需要数据库会话")

        results = {
            "total_processed": 0,
            "success": 0,
            "errors": [],
        }

        # 获取待分析内容（已通过预审）
        if content_id:
            content = await CRUD.get_content(session, content_id)
            contents = [content] if content and content.status == "reviewed" else []
        else:
            contents = await CRUD.list_contents(session, status="reviewed", limit=limit)

        # 初始化进度
        self._progress["total"] = len(contents)
        self._progress["processed"] = 0
        self._progress["success"] = 0
        self._progress["failed"] = 0
        self._progress["status"] = "running"

        logger.info(f"[{self.name}] 开始分析 {len(contents)} 条内容")

        for i, content in enumerate(contents):
            try:
                # 更新当前处理项
                self._progress["current_item"] = content.title[:50]
                
                await self._analyze_content(content, session)
                results["total_processed"] += 1
                results["success"] += 1
                self._progress["success"] += 1

                # 添加请求延迟，防止 429 限流（最后一个不需要延迟）
                if i < len(contents) - 1:
                    logger.debug(f"[{self.name}] 等待 {API_REQUEST_DELAY} 秒后继续...")
                    await asyncio.sleep(API_REQUEST_DELAY)

            except Exception as e:
                logger.error(f"[{self.name}] 分析失败: {content.title[:50]}, 错误: {e}")
                results["errors"].append(str(e))
                self._progress["failed"] += 1
                # 错误后也添加延迟
                if i < len(contents) - 1:
                    await asyncio.sleep(API_REQUEST_DELAY)
            
            finally:
                # 更新进度
                self._progress["processed"] = i + 1

        self._progress["status"] = "completed"
        logger.info(
            f"[{self.name}] 分析完成: 处理 {results['total_processed']}, "
            f"成功 {results['success']}"
        )

        return results

    async def _analyze_content(
        self,
        content: Content,
        session: AsyncSession,
    ) -> None:
        """
        分析单个内容

        Args:
            content: 待分析内容
            session: 数据库会话
        """
        # 获取预审记录
        review = await CRUD.get_review_by_content(session, content.id)
        
        # 生成总结
        summary_result = await self.summarizer.summarize(
            title=content.title,
            source=content.source,
            category=content.category,
            content=content.raw_content or content.summary or content.title,
        )

        # 分析知识关联
        knowledge_result = await self.knowledge_analyzer.analyze(
            title=content.title,
            summary=summary_result.summary,
            key_points=summary_result.key_points,
        )

        # 创建分析记录
        analysis = await CRUD.create_analysis(
            session=session,
            content_id=content.id,
            summary=summary_result.summary,
            key_points=summary_result.key_points,
            knowledge_links=[k.to_dict() for k in knowledge_result.knowledge_links],
            confusion_notes=[c.to_dict() for c in knowledge_result.confusion_notes],
            learning_suggestions=summary_result.learning_suggestions,
            related_topics=knowledge_result.related_topics,
        )

        # 创建学习记录（必须有review才能创建完整的学习记录）
        if review:
            await CRUD.create_learning_record(
                session=session,
                content=content,
                review=review,
                analysis=analysis,
            )
        else:
            # 如果没有review记录，创建一个默认的review记录
            logger.warning(f"[{self.name}] 内容没有预审记录，创建默认预审记录: {content.title[:30]}")
            default_review = await CRUD.create_review(
                session=session,
                content_id=content.id,
                novelty_score=60,
                utility_score=60,
                authority_score=60,
                timeliness_score=60,
                completeness_score=60,
                total_score=60.0,
                passed=True,
                review_notes="系统自动创建的默认预审记录",
            )
            await CRUD.create_learning_record(
                session=session,
                content=content,
                review=default_review,
                analysis=analysis,
            )

        # 更新内容状态
        await CRUD.update_content_status(session, content.id, "analyzed")

        logger.debug(f"[{self.name}] 分析完成: {content.title[:30]}")

    async def analyze_single(
        self,
        title: str,
        source: str,
        category: str,
        content: str,
    ) -> dict:
        """
        分析单个内容（不入库，用于测试）

        Args:
            title: 标题
            source: 来源
            category: 分类
            content: 内容

        Returns:
            完整分析结果
        """
        # 生成总结
        summary_result = await self.summarizer.summarize(
            title=title,
            source=source,
            category=category,
            content=content,
        )

        # 分析知识关联
        knowledge_result = await self.knowledge_analyzer.analyze(
            title=title,
            summary=summary_result.summary,
            key_points=summary_result.key_points,
        )

        return {
            "summary": summary_result.summary,
            "key_points": summary_result.key_points,
            "knowledge_links": [k.to_dict() for k in knowledge_result.knowledge_links],
            "confusion_notes": [c.to_dict() for c in knowledge_result.confusion_notes],
            "learning_suggestions": summary_result.learning_suggestions,
            "related_topics": knowledge_result.related_topics,
        }

    async def get_analyzed_contents(
        self,
        session: AsyncSession,
        category: Optional[str] = None,
        limit: int = 50,
    ) -> list[Content]:
        """
        获取已分析内容列表

        Args:
            session: 数据库会话
            category: 分类筛选
            limit: 最大数量

        Returns:
            已分析内容列表
        """
        return await CRUD.list_contents(
            session,
            status="analyzed",
            category=category,
            limit=limit,
        )
