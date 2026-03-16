"""异常模块单元测试"""
import pytest

from src.core.exceptions import (
    MetisError,
    ConfigurationError,
    MissingAPIKeyError,
    CollectionError,
    SourceConnectionError,
    SourceTimeoutError,
    ParseError,
    RateLimitError,
    ReviewError,
    ScoringError,
    ContentFilterError,
    AnalysisError,
    SummarizationError,
    KnowledgeLinkError,
    LLMError,
    LLMConnectionError,
    LLMResponseError,
    LLMRateLimitError,
    DatabaseError,
    RecordNotFoundError,
    DuplicateRecordError,
    APIError,
    ValidationError,
    AuthenticationError,
)


class TestMetisError:
    """基础异常类测试"""

    def test_basic_error(self):
        """测试基本错误"""
        error = MetisError("测试错误")
        
        assert error.message == "测试错误"
        assert error.details == {}
        assert str(error) == "测试错误"

    def test_error_with_details(self):
        """测试带详情的错误"""
        details = {"key": "value", "count": 42}
        error = MetisError("测试错误", details=details)
        
        assert error.message == "测试错误"
        assert error.details == details
        assert "key" in str(error)
        assert "value" in str(error)

    def test_inheritance(self):
        """测试异常继承"""
        error = ConfigurationError("配置错误")
        
        assert isinstance(error, MetisError)
        assert isinstance(error, Exception)


class TestSpecificExceptions:
    """特定异常类测试"""

    def test_configuration_errors(self):
        """测试配置相关异常"""
        error1 = ConfigurationError("配置失败")
        error2 = MissingAPIKeyError("缺少API密钥")
        
        assert isinstance(error1, MetisError)
        assert isinstance(error2, ConfigurationError)

    def test_collection_errors(self):
        """测试采集相关异常"""
        error1 = CollectionError("采集失败")
        error2 = SourceConnectionError("连接失败")
        error3 = SourceTimeoutError("超时")
        error4 = ParseError("解析失败")
        error5 = RateLimitError("频率限制")
        
        assert isinstance(error1, MetisError)
        assert isinstance(error2, CollectionError)
        assert isinstance(error3, CollectionError)
        assert isinstance(error4, CollectionError)
        assert isinstance(error5, CollectionError)

    def test_review_errors(self):
        """测试预审相关异常"""
        error1 = ReviewError("预审失败")
        error2 = ScoringError("评分失败")
        error3 = ContentFilterError("过滤失败")
        
        assert isinstance(error1, MetisError)
        assert isinstance(error2, ReviewError)
        assert isinstance(error3, ReviewError)

    def test_analysis_errors(self):
        """测试分析相关异常"""
        error1 = AnalysisError("分析失败")
        error2 = SummarizationError("总结失败")
        error3 = KnowledgeLinkError("关联失败")
        
        assert isinstance(error1, MetisError)
        assert isinstance(error2, AnalysisError)
        assert isinstance(error3, AnalysisError)

    def test_llm_errors(self):
        """测试LLM相关异常"""
        error1 = LLMError("LLM错误")
        error2 = LLMConnectionError("连接失败")
        error3 = LLMResponseError("响应错误")
        error4 = LLMRateLimitError("频率限制")
        
        assert isinstance(error1, MetisError)
        assert isinstance(error2, LLMError)
        assert isinstance(error3, LLMError)
        assert isinstance(error4, LLMError)

    def test_database_errors(self):
        """测试数据库相关异常"""
        error1 = DatabaseError("数据库错误")
        error2 = RecordNotFoundError("记录不存在")
        error3 = DuplicateRecordError("重复记录")
        
        assert isinstance(error1, MetisError)
        assert isinstance(error2, DatabaseError)
        assert isinstance(error3, DatabaseError)

    def test_api_errors(self):
        """测试API相关异常"""
        error1 = APIError("API错误")
        error2 = ValidationError("验证失败")
        error3 = AuthenticationError("认证失败")
        
        assert isinstance(error1, MetisError)
        assert isinstance(error2, APIError)
        assert isinstance(error3, APIError)