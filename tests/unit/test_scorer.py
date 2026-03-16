"""评分引擎测试"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agents.reviewer.scorer import Scorer, ScoreResult


class TestScorer:
    """评分引擎测试"""

    @pytest.fixture
    def mock_llm(self):
        """创建模拟LLM"""
        llm = MagicMock()
        llm.ainvoke = AsyncMock()
        return llm

    @pytest.fixture
    def scorer(self, mock_llm):
        """创建评分器实例"""
        return Scorer(mock_llm)

    def test_init(self, scorer):
        """测试初始化"""
        assert scorer.passing_score == 60
        assert "novelty" in scorer.weights
        assert scorer.weights["novelty"] == 0.25

    def test_calculate_weighted_score(self, scorer):
        """测试加权分数计算"""
        scores = {
            "novelty_score": 80,
            "utility_score": 70,
            "authority_score": 60,
            "timeliness_score": 50,
            "completeness_score": 40,
        }
        
        result = scorer._calculate_weighted_score(scores)
        
        # 80*0.25 + 70*0.25 + 60*0.20 + 50*0.15 + 40*0.15
        # = 20 + 17.5 + 12 + 7.5 + 6 = 63
        assert result == 63.0

    def test_parse_response_valid_json(self, scorer):
        """测试解析有效JSON响应"""
        response = '{"novelty_score": 80, "utility_score": 70}'
        result = scorer._parse_response(response)
        
        assert result["novelty_score"] == 80
        assert result["utility_score"] == 70

    def test_parse_response_json_in_text(self, scorer):
        """测试解析文本中的JSON"""
        response = '这是一些文本 {"novelty_score": 80} 更多的文本'
        result = scorer._parse_response(response)
        
        assert result["novelty_score"] == 80

    def test_parse_response_invalid(self, scorer):
        """测试解析无效响应"""
        response = "这不是JSON"
        result = scorer._parse_response(response)
        
        # 返回默认值
        assert result["novelty_score"] == 50
        assert result["utility_score"] == 50

    @pytest.mark.asyncio
    async def test_score_success(self, scorer, mock_llm):
        """测试成功评分"""
        mock_response = MagicMock()
        mock_response.content = '''
        {
            "novelty_score": 80,
            "utility_score": 70,
            "authority_score": 60,
            "timeliness_score": 50,
            "completeness_score": 40,
            "brief_reason": "测试评分"
        }
        '''
        mock_llm.ainvoke.return_value = mock_response
        
        result = await scorer.score(
            title="测试标题",
            source="arxiv",
            category="academic_ai",
            summary="测试摘要",
        )
        
        assert isinstance(result, ScoreResult)
        assert result.novelty_score == 80
        assert result.utility_score == 70
        assert result.total_score == 63.0
        assert result.passed is True
        assert result.brief_reason == "测试评分"

    @pytest.mark.asyncio
    async def test_score_below_threshold(self, scorer, mock_llm):
        """测试低于及格线"""
        mock_response = MagicMock()
        mock_response.content = '''
        {
            "novelty_score": 30,
            "utility_score": 30,
            "authority_score": 30,
            "timeliness_score": 30,
            "completeness_score": 30,
            "brief_reason": "质量较低"
        }
        '''
        mock_llm.ainvoke.return_value = mock_response
        
        result = await scorer.score(
            title="测试标题",
            source="arxiv",
            category="academic_ai",
            summary="测试摘要",
        )
        
        assert result.total_score == 30.0
        assert result.passed is False


class TestScoreResult:
    """评分结果测试"""

    def test_to_dict(self):
        """测试转换为字典"""
        result = ScoreResult(
            novelty_score=80,
            utility_score=70,
            authority_score=60,
            timeliness_score=50,
            completeness_score=40,
            total_score=63.0,
            passed=True,
            brief_reason="测试",
        )
        
        d = result.to_dict()
        
        assert d["novelty_score"] == 80
        assert d["total_score"] == 63.0
        assert d["passed"] is True