"""Pytest配置"""
import pytest
import asyncio
from pathlib import Path
import sys

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config():
    """测试配置fixture"""
    return {
        "test_mode": True,
        "mock_llm": True,
    }


@pytest.fixture
def sample_content():
    """示例内容fixture"""
    return {
        "id": "test-content-id",
        "title": "Test Paper Title",
        "source": "arxiv",
        "source_url": "https://arxiv.org/abs/1234.5678",
        "category": "academic_ai",
        "summary": "This is a test summary for the paper.",
        "status": "pending",
    }


@pytest.fixture
def sample_review():
    """示例预审fixture"""
    return {
        "id": "test-review-id",
        "content_id": "test-content-id",
        "novelty_score": 80,
        "utility_score": 70,
        "authority_score": 60,
        "timeliness_score": 50,
        "completeness_score": 40,
        "total_score": 63.0,
        "passed": True,
    }


@pytest.fixture
def sample_analysis():
    """示例分析fixture"""
    return {
        "id": "test-analysis-id",
        "content_id": "test-content-id",
        "summary": "这是核心总结",
        "key_points": ["要点1", "要点2", "要点3"],
        "knowledge_links": [
            {"concept": "深度学习", "relation": "先修", "note": "需要了解基础概念"}
        ],
        "confusion_notes": [
            {"item": "CNN vs RNN", "distinction": "前者处理空间数据，后者处理序列数据"}
        ],
    }