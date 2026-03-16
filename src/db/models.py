"""数据库模型定义"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类"""
    pass


def generate_uuid() -> str:
    """生成 UUID 字符串"""
    return str(uuid.uuid4())


class Content(Base):
    """采集内容模型"""

    __tablename__ = "contents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    
    # 基本信息
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)  # arxiv, hackernews, reddit
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # academic_ai, news_security 等
    
    # 内容
    raw_content: Mapped[str] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 原始摘要
    
    # 元数据
    authors: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON 数组
    published_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON 数组
    
    # 状态
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="pending"
    )  # pending, reviewed, analyzed, rejected
    
    # 时间戳
    collected_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Content(id={self.id}, title={self.title[:30]}..., status={self.status})>"


class Review(Base):
    """预审记录模型"""

    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    
    # 评分 (各项 0-100)
    novelty_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 新颖性
    utility_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 实用性
    authority_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 权威性
    timeliness_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 时效性
    completeness_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 完整性
    
    # 总分
    total_score: Mapped[float] = mapped_column(Float, nullable=False)  # 加权总分
    
    # 结果
    passed: Mapped[bool] = mapped_column(Integer, nullable=False)  # 是否通过预审
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 预审备注
    
    # 时间戳
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, content_id={self.content_id}, total_score={self.total_score}, passed={self.passed})>"


class Analysis(Base):
    """分析结果模型"""

    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    
    # 总结
    summary: Mapped[str] = mapped_column(Text, nullable=False)  # 核心总结
    
    # 要点 (JSON 数组)
    key_points: Mapped[str] = mapped_column(Text, nullable=False)  # JSON: ["要点1", "要点2", ...]
    
    # 知识关联 (JSON 数组)
    knowledge_links: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # JSON: [{"concept": "关联概念", "relation": "关系说明", "note": "辨析提醒"}, ...]
    
    # 易混淆辨析 (JSON 数组)
    confusion_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # JSON: [{"item": "易混淆内容", "distinction": "区分要点"}, ...]
    
    # 学习建议
    learning_suggestions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 关联主题标签
    related_topics: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON 数组
    
    # 时间戳
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Analysis(id={self.id}, content_id={self.content_id})>"


class CollectionJob(Base):
    """采集任务模型"""

    __tablename__ = "collection_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    
    # 任务信息
    source: Mapped[str] = mapped_column(String(100), nullable=False)  # 数据源
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="pending"
    )  # pending, running, completed, failed
    
    # 统计
    items_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    items_collected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    items_deduplicated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # 错误信息
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 时间戳
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<CollectionJob(id={self.id}, source={self.source}, status={self.status})>"


class LearningRecord(Base):
    """学习记录模型 - 最终输出"""

    __tablename__ = "learning_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    
    # 关联
    content_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    review_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    analysis_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # 基本信息 (冗余存储便于查询)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    
    # 评分
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    
    # 分析结果 (冗余存储)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    key_points: Mapped[str] = mapped_column(Text, nullable=False)
    knowledge_links: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confusion_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    learning_suggestions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 用户标记
    is_read: Mapped[bool] = mapped_column(Integer, nullable=False, default=False)
    is_bookmarked: Mapped[bool] = mapped_column(Integer, nullable=False, default=False)
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<LearningRecord(id={self.id}, title={self.title[:30]}...)>"
