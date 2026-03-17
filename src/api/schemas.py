"""API 数据模型定义"""
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


# ==================== 通用响应模型 ====================

class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = True
    message: str = "操作成功"


# ==================== 内容相关模型 ====================

class ContentBase(BaseModel):
    """内容基础模型"""
    title: str
    source: str
    source_url: str
    category: str
    summary: Optional[str] = None


class ContentCreate(ContentBase):
    """创建内容请求模型"""
    raw_content: Optional[str] = None
    authors: Optional[list[str]] = None
    tags: Optional[list[str]] = None


class ContentResponse(ContentBase):
    """内容响应模型"""
    id: str
    status: str
    authors: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    collected_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentListResponse(BaseResponse):
    """内容列表响应"""
    data: list[ContentResponse]
    total: int
    page: int
    page_size: int


# ==================== 预审相关模型 ====================

class ScoreDetail(BaseModel):
    """评分详情"""
    novelty_score: int = Field(..., ge=0, le=100)
    utility_score: int = Field(..., ge=0, le=100)
    authority_score: int = Field(..., ge=0, le=100)
    timeliness_score: int = Field(..., ge=0, le=100)
    completeness_score: int = Field(..., ge=0, le=100)


class ReviewResponse(BaseModel):
    """预审响应模型"""
    id: str
    content_id: str
    total_score: float
    passed: bool
    score_detail: ScoreDetail
    review_notes: Optional[str] = None
    reviewed_at: datetime

    class Config:
        from_attributes = True


class ReviewRequest(BaseModel):
    """预审请求模型"""
    content_id: Optional[str] = None  # 可选，为空则处理所有待预审内容


class ReviewListResponse(BaseResponse):
    """预审列表响应"""
    data: list[ReviewResponse]
    total: int


# ==================== 分析相关模型 ====================

class KnowledgeLink(BaseModel):
    """知识关联"""
    concept: str
    relation: str
    note: str


class ConfusionNote(BaseModel):
    """易混淆辨析"""
    item: str
    distinction: str


class AnalysisResponse(BaseModel):
    """分析响应模型"""
    id: str
    content_id: str
    summary: str
    key_points: list[str]
    knowledge_links: Optional[list[KnowledgeLink]] = None
    confusion_notes: Optional[list[ConfusionNote]] = None
    learning_suggestions: Optional[str] = None
    related_topics: Optional[list[str]] = None
    analyzed_at: datetime

    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    """分析请求模型"""
    content_id: Optional[str] = None  # 可选，为空则处理所有待分析内容


class AnalysisListResponse(BaseResponse):
    """分析列表响应"""
    data: list[AnalysisResponse]
    total: int


# ==================== 学习记录相关模型 ====================

class LearningRecordResponse(BaseModel):
    """学习记录响应模型"""
    id: str
    title: str
    category: str
    source: str
    source_url: str
    total_score: float
    summary: str
    key_points: list[str]
    knowledge_links: Optional[list[KnowledgeLink]] = None
    confusion_notes: Optional[list[ConfusionNote]] = None
    learning_suggestions: Optional[str] = None
    is_read: bool = False
    is_bookmarked: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class LearningRecordListResponse(BaseResponse):
    """学习记录列表响应"""
    data: list[LearningRecordResponse]
    total: int
    page: int
    page_size: int


class LearningRecordUpdate(BaseModel):
    """更新学习记录请求"""
    is_read: Optional[bool] = None
    is_bookmarked: Optional[bool] = None
    user_notes: Optional[str] = None


# ==================== 采集相关模型 ====================

class CollectRequest(BaseModel):
    """采集请求模型"""
    sources: Optional[list[str]] = None
    limit_per_source: Optional[int] = Field(None, ge=1, le=100)


class CollectResult(BaseModel):
    """采集结果模型"""
    total_found: int
    total_collected: int
    total_deduplicated: int
    by_source: dict[str, dict[str, int]]
    errors: list[str]


class CollectResponse(BaseResponse):
    """采集响应模型"""
    data: CollectResult


# ==================== 流水线相关模型 ====================

class PipelineRequest(BaseModel):
    """流水线请求模型"""
    collect: bool = True
    review: bool = True
    analyze: bool = True
    limit: int = Field(20, ge=1, le=100)


class PipelineResult(BaseModel):
    """流水线结果模型"""
    collect: Optional[CollectResult] = None
    review: Optional[dict[str, Any]] = None
    analyze: Optional[dict[str, Any]] = None


class PipelineResponse(BaseResponse):
    """流水线响应模型"""
    data: PipelineResult


# ==================== 系统状态模型 ====================

class SystemStatus(BaseModel):
    """系统状态模型"""
    app_name: str
    version: str
    status: str = "running"
    database_connected: bool = True
    llm_configured: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SystemStatusResponse(BaseResponse):
    """系统状态响应"""
    data: SystemStatus
