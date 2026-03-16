"""数据源适配器测试"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from src.agents.collector.sources.base import BaseSource, CollectedItem
from src.agents.collector.sources.arxiv import ArxivSource
from src.agents.collector.sources.news import HackerNewsSource, RedditSource, NewsSourceFactory


class TestCollectedItem:
    """CollectedItem 数据类测试"""

    def test_basic_item(self):
        """测试基本数据项"""
        item = CollectedItem(
            title="测试标题",
            source="test",
            source_url="https://example.com",
            category="academic_ai",
        )
        
        assert item.title == "测试标题"
        assert item.source == "test"
        assert item.source_url == "https://example.com"
        assert item.category == "academic_ai"
        assert item.raw_content is None
        assert item.summary is None

    def test_full_item(self):
        """测试完整数据项"""
        published = datetime(2024, 1, 1)
        item = CollectedItem(
            title="测试标题",
            source="arxiv",
            source_url="https://arxiv.org/abs/1234",
            category="academic_ai",
            raw_content="原始内容",
            summary="摘要",
            authors=["作者1", "作者2"],
            published_date=published,
            tags=["AI", "ML"],
            metadata={"key": "value"},
        )
        
        assert item.raw_content == "原始内容"
        assert item.summary == "摘要"
        assert len(item.authors) == 2
        assert item.published_date == published
        assert len(item.tags) == 2

    def test_to_dict(self):
        """测试转换为字典"""
        item = CollectedItem(
            title="测试标题",
            source="test",
            source_url="https://example.com",
            category="academic_ai",
        )
        
        result = item.to_dict()
        
        assert isinstance(result, dict)
        assert result["title"] == "测试标题"
        assert result["source"] == "test"


class TestArxivSource:
    """arXiv 数据源测试"""

    def test_init(self):
        """测试初始化"""
        source = ArxivSource()
        
        assert source.name == "arxiv"
        assert "cs.AI" in source.config.get("categories", [])

    def test_category_mapping(self):
        """测试分类映射"""
        source = ArxivSource()
        
        assert source._map_category("cs.AI") == "academic_ai"
        assert source._map_category("cs.CR") == "academic_security"
        assert source._map_category("cs.UNKNOWN") == "academic_ai"  # 默认


class TestHackerNewsSource:
    """HackerNews 数据源测试"""

    def test_init(self):
        """测试初始化"""
        source = HackerNewsSource()
        
        assert source.name == "hackernews"
        assert source.base_url == "https://hacker-news.firebaseio.com/v0"


class TestRedditSource:
    """Reddit 数据源测试"""

    def test_init_ml(self):
        """测试初始化 - ML板块"""
        source = RedditSource(subreddit_type="reddit_ml")
        
        assert source.name == "reddit_ml"
        assert source.subreddit_type == "reddit_ml"

    def test_init_security(self):
        """测试初始化 - 安全板块"""
        source = RedditSource(subreddit_type="reddit_security")
        
        assert source.name == "reddit_security"

    def test_subreddit_config(self):
        """测试板块配置"""
        config = RedditSource.SUBREDDIT_CONFIG
        
        assert "reddit_ml" in config
        assert config["reddit_ml"]["subreddit"] == "MachineLearning"
        assert "reddit_security" in config


class TestNewsSourceFactory:
    """新闻源工厂测试"""

    def test_create_hackernews(self):
        """测试创建 HackerNews 源"""
        source = NewsSourceFactory.create("hackernews")
        
        assert isinstance(source, HackerNewsSource)

    def test_create_reddit_ml(self):
        """测试创建 Reddit ML 源"""
        source = NewsSourceFactory.create("reddit_ml")
        
        assert isinstance(source, RedditSource)
        assert source.subreddit_type == "reddit_ml"

    def test_create_unknown(self):
        """测试创建未知源"""
        with pytest.raises(ValueError, match="未知的新闻源"):
            NewsSourceFactory.create("unknown_source")