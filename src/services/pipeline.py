"""处理流水线服务"""
import asyncio
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.collector.agent import CollectorAgent
from src.agents.reviewer.agent import ReviewerAgent
from src.agents.analyzer.agent import AnalyzerAgent
from src.db.crud import db
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class Pipeline:
    """
    处理流水线
    
    串联三个智能体的处理流程：采集 → 预审 → 分析
    """

    def __init__(self):
        self.collector = CollectorAgent()
        self.reviewer = ReviewerAgent()
        self.analyzer = AnalyzerAgent()

    async def run(
        self,
        collect: bool = True,
        review: bool = True,
        analyze: bool = True,
        limit: int = 20,
        sources: Optional[list[str]] = None,
    ) -> dict:
        """
        执行完整流水线

        Args:
            collect: 是否执行采集
            review: 是否执行预审
            analyze: 是否执行分析
            limit: 每个阶段的最大处理数量
            sources: 指定采集源

        Returns:
            流水线执行结果
        """
        results = {
            "collect": None,
            "review": None,
            "analyze": None,
        }

        async with db.async_session() as session:
            # 阶段1: 采集
            if collect:
                logger.info("[Pipeline] 开始采集阶段...")
                results["collect"] = await self.collector.run(
                    source_names=sources,
                    limit_per_source=limit,
                    session=session,
                )
                logger.info(f"[Pipeline] 采集完成: {results['collect']['total_collected']} 条")

            # 阶段2: 预审
            if review:
                logger.info("[Pipeline] 开始预审阶段...")
                results["review"] = await self.reviewer.run(
                    session=session,
                    limit=limit,
                )
                logger.info(f"[Pipeline] 预审完成: 通过 {results['review']['passed']} 条")

            # 阶段3: 分析
            if analyze:
                logger.info("[Pipeline] 开始分析阶段...")
                results["analyze"] = await self.analyzer.run(
                    session=session,
                    limit=limit,
                )
                logger.info(f"[Pipeline] 分析完成: {results['analyze']['success']} 条")

        return results

    async def run_single_content(
        self,
        content_id: str,
        skip_collect: bool = True,
    ) -> dict:
        """
        对单个内容执行流水线

        Args:
            content_id: 内容ID
            skip_collect: 是否跳过采集（默认跳过，因为内容已存在）

        Returns:
            执行结果
        """
        results = {
            "collect": None,
            "review": None,
            "analyze": None,
        }

        async with db.async_session() as session:
            if not skip_collect:
                # 如果需要采集，这里应该先执行采集逻辑
                pass

            # 预审
            results["review"] = await self.reviewer.run(
                content_id=content_id,
                session=session,
            )

            # 分析
            results["analyze"] = await self.analyzer.run(
                content_id=content_id,
                session=session,
            )

        return results


# 导出实例
pipeline = Pipeline()
