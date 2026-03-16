"""自定义异常模块"""


class MetisError(Exception):
    """Metis_ParseBot 基础异常类"""

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


# ==================== 配置相关异常 ====================

class ConfigurationError(MetisError):
    """配置错误"""
    pass


class MissingAPIKeyError(ConfigurationError):
    """API Key 缺失错误"""
    pass


# ==================== 采集相关异常 ====================

class CollectionError(MetisError):
    """采集错误基类"""
    pass


class SourceConnectionError(CollectionError):
    """数据源连接错误"""
    pass


class SourceTimeoutError(CollectionError):
    """数据源超时错误"""
    pass


class ParseError(CollectionError):
    """内容解析错误"""
    pass


class RateLimitError(CollectionError):
    """频率限制错误"""
    pass


# ==================== 预审相关异常 ====================

class ReviewError(MetisError):
    """预审错误基类"""
    pass


class ScoringError(ReviewError):
    """评分错误"""
    pass


class ContentFilterError(ReviewError):
    """内容过滤错误"""
    pass


# ==================== 分析相关异常 ====================

class AnalysisError(MetisError):
    """分析错误基类"""
    pass


class SummarizationError(AnalysisError):
    """总结生成错误"""
    pass


class KnowledgeLinkError(AnalysisError):
    """知识关联错误"""
    pass


# ==================== LLM 相关异常 ====================

class LLMError(MetisError):
    """LLM 调用错误基类"""
    pass


class LLMConnectionError(LLMError):
    """LLM 连接错误"""
    pass


class LLMResponseError(LLMError):
    """LLM 响应错误"""
    pass


class LLMRateLimitError(LLMError):
    """LLM 频率限制错误"""
    pass


# ==================== 数据库相关异常 ====================

class DatabaseError(MetisError):
    """数据库错误基类"""
    pass


class RecordNotFoundError(DatabaseError):
    """记录未找到错误"""
    pass


class DuplicateRecordError(DatabaseError):
    """重复记录错误"""
    pass


# ==================== API 相关异常 ====================

class APIError(MetisError):
    """API 错误基类"""
    pass


class ValidationError(APIError):
    """数据验证错误"""
    pass


class AuthenticationError(APIError):
    """认证错误"""
    pass
