"""数据源适配器基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class CollectedItem:
    """采集内容项"""
    title: str
    source: str  # 数据源名称
    source_url: str  # 原始链接
    category: str  # 分类标签
    raw_content: Optional[str] = None
    summary: Optional[str] = None
    authors: Optional[list[str]] = None
    published_date: Optional[datetime] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "title": self.title,
            "source": self.source,
            "source_url": self.source_url,
            "category": self.category,
            "raw_content": self.raw_content,
            "summary": self.summary,
            "authors": self.authors,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "tags": self.tags,
            "metadata": self.metadata,
        }


class BaseSource(ABC):
    """数据源适配器基类"""

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.config = kwargs

    @abstractmethod
    async def fetch(self, limit: int = 20) -> list[CollectedItem]:
        """
        从数据源获取内容

        Args:
            limit: 最大获取数量

        Returns:
            采集的内容列表
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"
