"""arXiv 数据源适配器"""
from datetime import datetime
from typing import Optional

import arxiv

from src.agents.collector.sources.base import BaseSource, CollectedItem
from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import SourceConnectionError, ParseError

logger = get_logger(__name__)


class ArxivSource(BaseSource):
    """arXiv 学术论文数据源"""

    # arXiv 分类到系统分类的映射
    CATEGORY_MAP = {
        "cs.AI": "academic_ai",
        "cs.CL": "academic_ai",
        "cs.LG": "academic_ai",
        "cs.CV": "academic_ai",
        "cs.RO": "academic_ai",
        "cs.CR": "academic_security",
        "cs.SE": "academic_security",
        "cs.NI": "academic_security",
    }

    def __init__(
        self,
        categories: Optional[list[str]] = None,
        max_results: Optional[int] = None,
    ):
        super().__init__(
            name="arxiv",
            categories=categories or settings.arxiv_categories,
            max_results=max_results or settings.arxiv_max_results,
        )

    async def fetch(self, limit: int = 20) -> list[CollectedItem]:
        """
        从 arXiv 获取最新论文

        Args:
            limit: 最大获取数量

        Returns:
            论文列表
        """
        actual_limit = min(limit, self.config.get("max_results", settings.arxiv_max_results))
        categories = self.config.get("categories", settings.arxiv_categories)
        
        items = []
        
        try:
            # 构建查询
            query = " OR ".join([f"cat:{cat}" for cat in categories])
            logger.info(f"[arXiv] 开始查询: {query}")
            
            # 执行搜索
            search = arxiv.Search(
                query=query,
                max_results=actual_limit,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )
            
            for result in search.results():
                try:
                    item = self._parse_result(result)
                    items.append(item)
                except Exception as e:
                    logger.warning(f"[arXiv] 解析论文失败: {result.entry_id}, 错误: {e}")
                    continue
            
            logger.info(f"[arXiv] 成功获取 {len(items)} 篇论文")
            
        except Exception as e:
            logger.error(f"[arXiv] 获取论文失败: {e}")
            raise SourceConnectionError(f"arXiv 连接失败: {e}")

        return items

    def _parse_result(self, result: arxiv.Result) -> CollectedItem:
        """解析 arXiv 结果"""
        # 确定分类
        primary_category = result.primary_category or "cs.AI"
        category = self._map_category(primary_category)

        # 提取作者
        authors = [author.name for author in result.authors] if result.authors else None

        # 构建标签
        tags = [cat for cat in result.categories] if result.categories else []
        tags.append(primary_category)

        return CollectedItem(
            title=result.title,
            source="arxiv",
            source_url=result.entry_id,
            category=category,
            raw_content=result.summary,
            summary=result.summary,
            authors=authors,
            published_date=result.published,
            tags=list(set(tags)),
            metadata={
                "arxiv_id": result.entry_id.split("/")[-1],
                "primary_category": primary_category,
                "pdf_url": result.pdf_url,
                "comment": result.comment,
                "journal_ref": result.journal_ref,
            },
        )

    def _map_category(self, arxiv_category: str) -> str:
        """将 arXiv 分类映射到系统分类"""
        # 精确匹配
        if arxiv_category in self.CATEGORY_MAP:
            return self.CATEGORY_MAP[arxiv_category]
        
        # 前缀匹配
        for key, value in self.CATEGORY_MAP.items():
            if arxiv_category.startswith(key.split(".")[0] + "."):
                return value
        
        # 默认分类
        return "academic_ai"
