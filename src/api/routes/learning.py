"""学习记录路由"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import json

from src.api.schemas import (
    LearningRecordResponse,
    LearningRecordListResponse,
    LearningRecordUpdate,
    KnowledgeLink,
    ConfusionNote,
    BaseResponse,
)
from src.db.crud import CRUD, db
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/learning", tags=["学习记录"])


async def get_session():
    """获取数据库会话"""
    async with db.async_session() as session:
        yield session


@router.get("", response_model=LearningRecordListResponse)
async def list_learning_records(
    category: Optional[str] = Query(None, description="分类筛选"),
    is_read: Optional[bool] = Query(None, description="已读筛选"),
    is_bookmarked: Optional[bool] = Query(None, description="收藏筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    session: AsyncSession = Depends(get_session),
):
    """获取学习记录列表"""
    offset = (page - 1) * page_size
    records = await CRUD.list_learning_records(
        session,
        category=category,
        is_read=is_read,
        is_bookmarked=is_bookmarked,
        limit=page_size,
        offset=offset,
    )
    
    # 转换为响应格式
    data = []
    for record in records:
        knowledge_links = None
        if record.knowledge_links:
            links_data = json.loads(record.knowledge_links)
            knowledge_links = [KnowledgeLink(**link) for link in links_data]
        
        confusion_notes = None
        if record.confusion_notes:
            notes_data = json.loads(record.confusion_notes)
            confusion_notes = [ConfusionNote(**note) for note in notes_data]
        
        data.append(LearningRecordResponse(
            id=record.id,
            title=record.title,
            category=record.category,
            source=record.source,
            source_url=record.source_url,
            total_score=record.total_score,
            summary=record.summary,
            key_points=json.loads(record.key_points) if record.key_points else [],
            knowledge_links=knowledge_links,
            confusion_notes=confusion_notes,
            learning_suggestions=record.learning_suggestions,
            is_read=record.is_read,
            is_bookmarked=record.is_bookmarked,
            created_at=record.created_at,
        ))
    
    return LearningRecordListResponse(
        data=data,
        total=len(data),
        page=page,
        page_size=page_size,
    )


@router.get("/{record_id}", response_model=LearningRecordResponse)
async def get_learning_record(
    record_id: str,
    session: AsyncSession = Depends(get_session),
):
    """获取单个学习记录详情"""
    # 查询学习记录
    from sqlalchemy import select
    from src.db.models import LearningRecord
    
    result = await session.execute(
        select(LearningRecord).where(LearningRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="学习记录不存在")
    
    knowledge_links = None
    if record.knowledge_links:
        links_data = json.loads(record.knowledge_links)
        knowledge_links = [KnowledgeLink(**link) for link in links_data]
    
    confusion_notes = None
    if record.confusion_notes:
        notes_data = json.loads(record.confusion_notes)
        confusion_notes = [ConfusionNote(**note) for note in notes_data]
    
    return LearningRecordResponse(
        id=record.id,
        title=record.title,
        category=record.category,
        source=record.source,
        source_url=record.source_url,
        total_score=record.total_score,
        summary=record.summary,
        key_points=json.loads(record.key_points) if record.key_points else [],
        knowledge_links=knowledge_links,
        confusion_notes=confusion_notes,
        learning_suggestions=record.learning_suggestions,
        is_read=record.is_read,
        is_bookmarked=record.is_bookmarked,
        created_at=record.created_at,
    )


@router.patch("/{record_id}", response_model=BaseResponse)
async def update_learning_record(
    record_id: str,
    update_data: LearningRecordUpdate,
    session: AsyncSession = Depends(get_session),
):
    """更新学习记录（标记已读、收藏等）"""
    from sqlalchemy import select, update
    from src.db.models import LearningRecord
    
    # 查询记录
    result = await session.execute(
        select(LearningRecord).where(LearningRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="学习记录不存在")
    
    # 更新字段
    if update_data.is_read is not None:
        record.is_read = update_data.is_read
    if update_data.is_bookmarked is not None:
        record.is_bookmarked = update_data.is_bookmarked
    if update_data.user_notes is not None:
        record.user_notes = update_data.user_notes
    
    await session.commit()
    
    return BaseResponse(message="更新成功")


@router.delete("/{record_id}", response_model=BaseResponse)
async def delete_learning_record(
    record_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除学习记录"""
    from sqlalchemy import select
    from src.db.models import LearningRecord
    
    result = await session.execute(
        select(LearningRecord).where(LearningRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="学习记录不存在")
    
    await session.delete(record)
    await session.commit()
    
    return BaseResponse(message="删除成功")
