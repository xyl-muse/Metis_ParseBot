"""数据库 CRUD 操作"""
import json
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload

from src.core.config import settings
from src.core.exceptions import RecordNotFoundError, DuplicateRecordError
from src.db.models import Base, Content, Review, Analysis, CollectionJob, LearningRecord


class Database:
    """数据库管理类"""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or settings.database_url
        self.engine = create_async_engine(
            self.database_url,
            echo=settings.database_echo,
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def create_tables(self) -> None:
        """创建所有表"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """删除所有表（仅用于测试）"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_session(self) -> AsyncSession:
        """获取数据库会话"""
        return self.async_session()


class CRUD:
    """CRUD 操作类"""

    # ==================== Content 操作 ====================

    @staticmethod
    async def create_content(
        session: AsyncSession,
        title: str,
        source: str,
        source_url: str,
        category: str,
        raw_content: Optional[str] = None,
        summary: Optional[str] = None,
        authors: Optional[list[str]] = None,
        published_date: Optional[datetime] = None,
        tags: Optional[list[str]] = None,
    ) -> Content:
        """创建内容记录"""
        content = Content(
            title=title,
            source=source,
            source_url=source_url,
            category=category,
            raw_content=raw_content,
            summary=summary,
            authors=json.dumps(authors) if authors else None,
            published_date=published_date,
            tags=json.dumps(tags) if tags else None,
        )
        session.add(content)
        await session.commit()
        await session.refresh(content)
        return content

    @staticmethod
    async def get_content(session: AsyncSession, content_id: str) -> Optional[Content]:
        """获取单个内容"""
        result = await session.execute(
            select(Content).where(Content.id == content_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_content_by_url(session: AsyncSession, source_url: str) -> Optional[Content]:
        """根据 URL 获取内容（用于去重）"""
        result = await session.execute(
            select(Content).where(Content.source_url == source_url)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_contents(
        session: AsyncSession,
        status: Optional[str] = None,
        category: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Content]:
        """获取内容列表"""
        query = select(Content)
        
        conditions = []
        if status:
            conditions.append(Content.status == status)
        if category:
            conditions.append(Content.category == category)
        if source:
            conditions.append(Content.source == source)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Content.collected_at.desc()).offset(offset).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_content_status(
        session: AsyncSession,
        content_id: str,
        status: str,
    ) -> Content:
        """更新内容状态"""
        content = await CRUD.get_content(session, content_id)
        if not content:
            raise RecordNotFoundError(f"Content not found: {content_id}")
        content.status = status
        await session.commit()
        await session.refresh(content)
        return content

    # ==================== Review 操作 ====================

    @staticmethod
    async def create_review(
        session: AsyncSession,
        content_id: str,
        novelty_score: int,
        utility_score: int,
        authority_score: int,
        timeliness_score: int,
        completeness_score: int,
        total_score: float,
        passed: bool,
        review_notes: Optional[str] = None,
    ) -> Review:
        """创建预审记录"""
        review = Review(
            content_id=content_id,
            novelty_score=novelty_score,
            utility_score=utility_score,
            authority_score=authority_score,
            timeliness_score=timeliness_score,
            completeness_score=completeness_score,
            total_score=total_score,
            passed=passed,
            review_notes=review_notes,
        )
        session.add(review)
        await session.commit()
        await session.refresh(review)
        return review

    @staticmethod
    async def get_review_by_content(session: AsyncSession, content_id: str) -> Optional[Review]:
        """根据内容ID获取预审记录"""
        result = await session.execute(
            select(Review).where(Review.content_id == content_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_passed_reviews(
        session: AsyncSession,
        limit: int = 50,
    ) -> list[Review]:
        """获取通过预审的内容列表（按分数降序）"""
        result = await session.execute(
            select(Review)
            .where(Review.passed == True)
            .order_by(Review.total_score.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    # ==================== Analysis 操作 ====================

    @staticmethod
    async def create_analysis(
        session: AsyncSession,
        content_id: str,
        summary: str,
        key_points: list[str],
        knowledge_links: Optional[list[dict]] = None,
        confusion_notes: Optional[list[dict]] = None,
        learning_suggestions: Optional[str] = None,
        related_topics: Optional[list[str]] = None,
    ) -> Analysis:
        """创建分析记录"""
        analysis = Analysis(
            content_id=content_id,
            summary=summary,
            key_points=json.dumps(key_points, ensure_ascii=False),
            knowledge_links=json.dumps(knowledge_links, ensure_ascii=False) if knowledge_links else None,
            confusion_notes=json.dumps(confusion_notes, ensure_ascii=False) if confusion_notes else None,
            learning_suggestions=learning_suggestions,
            related_topics=json.dumps(related_topics, ensure_ascii=False) if related_topics else None,
        )
        session.add(analysis)
        await session.commit()
        await session.refresh(analysis)
        return analysis

    @staticmethod
    async def get_analysis_by_content(session: AsyncSession, content_id: str) -> Optional[Analysis]:
        """根据内容ID获取分析记录"""
        result = await session.execute(
            select(Analysis).where(Analysis.content_id == content_id)
        )
        return result.scalar_one_or_none()

    # ==================== CollectionJob 操作 ====================

    @staticmethod
    async def create_collection_job(
        session: AsyncSession,
        source: str,
    ) -> CollectionJob:
        """创建采集任务"""
        job = CollectionJob(source=source)
        session.add(job)
        await session.commit()
        await session.refresh(job)
        return job

    @staticmethod
    async def update_collection_job(
        session: AsyncSession,
        job_id: str,
        status: Optional[str] = None,
        items_found: Optional[int] = None,
        items_collected: Optional[int] = None,
        items_deduplicated: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> CollectionJob:
        """更新采集任务"""
        result = await session.execute(
            select(CollectionJob).where(CollectionJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            raise RecordNotFoundError(f"CollectionJob not found: {job_id}")
        
        if status is not None:
            job.status = status
        if items_found is not None:
            job.items_found = items_found
        if items_collected is not None:
            job.items_collected = items_collected
        if items_deduplicated is not None:
            job.items_deduplicated = items_deduplicated
        if error_message is not None:
            job.error_message = error_message
        
        if status == "running":
            job.started_at = datetime.utcnow()
        elif status in ("completed", "failed"):
            job.completed_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(job)
        return job

    # ==================== LearningRecord 操作 ====================

    @staticmethod
    async def create_learning_record(
        session: AsyncSession,
        content: Content,
        review: Review,
        analysis: Analysis,
    ) -> LearningRecord:
        """创建学习记录"""
        record = LearningRecord(
            content_id=content.id,
            review_id=review.id,
            analysis_id=analysis.id,
            title=content.title,
            category=content.category,
            source=content.source,
            source_url=content.source_url,
            total_score=review.total_score,
            summary=analysis.summary,
            key_points=analysis.key_points,
            knowledge_links=analysis.knowledge_links,
            confusion_notes=analysis.confusion_notes,
            learning_suggestions=analysis.learning_suggestions,
        )
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record

    @staticmethod
    async def list_learning_records(
        session: AsyncSession,
        category: Optional[str] = None,
        is_read: Optional[bool] = None,
        is_bookmarked: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[LearningRecord]:
        """获取学习记录列表"""
        query = select(LearningRecord)
        
        conditions = []
        if category:
            conditions.append(LearningRecord.category == category)
        if is_read is not None:
            conditions.append(LearningRecord.is_read == is_read)
        if is_bookmarked is not None:
            conditions.append(LearningRecord.is_bookmarked == is_bookmarked)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(LearningRecord.created_at.desc()).offset(offset).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())


# 导出实例
db = Database()
