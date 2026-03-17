"""学习记录路由"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
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
from src.db.models import LearningRecord, Content, Review, Analysis
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
    from sqlalchemy import select, func, and_
    from src.db.models import LearningRecord
    
    offset = (page - 1) * page_size
    
    # 构建查询条件
    conditions = []
    if category:
        conditions.append(LearningRecord.category == category)
    if is_read is not None:
        conditions.append(LearningRecord.is_read == is_read)
    if is_bookmarked is not None:
        conditions.append(LearningRecord.is_bookmarked == is_bookmarked)
    
    # 获取总数
    count_stmt = select(func.count()).select_from(LearningRecord)
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    total_result = await session.execute(count_stmt)
    total = total_result.scalar() or 0
    
    # 获取数据（按分数降序排列）
    stmt = select(LearningRecord).order_by(LearningRecord.total_score.desc())
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.offset(offset).limit(page_size)
    
    result = await session.execute(stmt)
    records = list(result.scalars().all())
    
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
        total=total,
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
    result = await session.execute(
        select(LearningRecord).where(LearningRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(status_code=404, detail="学习记录不存在")
    
    await session.delete(record)
    await session.commit()
    
    return BaseResponse(message="删除成功")


@router.post("/fix-consistency", response_model=BaseResponse)
async def fix_data_consistency():
    """
    修复数据一致性问题：
    1. 为已分析但没有学习记录的内容创建学习记录
    2. 清理孤立的预审记录
    """
    fixed_count = 0
    deleted_count = 0
    errors = []
    
    try:
        async with db.async_session() as session:
            # 1. 查找已分析但没有学习记录的内容
            result = await session.execute(
                select(Content).where(Content.status == "analyzed")
            )
            analyzed_contents = list(result.scalars().all())
            logger.info(f"找到 {len(analyzed_contents)} 条已分析内容")
            
            for content in analyzed_contents:
                try:
                    # 检查是否已有学习记录
                    lr_result = await session.execute(
                        select(LearningRecord).where(LearningRecord.content_id == content.id)
                    )
                    existing_lr = lr_result.scalar_one_or_none()
                    
                    if existing_lr:
                        continue
                    
                    # 获取预审和分析记录
                    review = await CRUD.get_review_by_content(session, content.id)
                    analysis = await CRUD.get_analysis_by_content(session, content.id)
                    
                    if not analysis:
                        logger.warning(f"内容 {content.id} 没有分析记录，跳过")
                        continue
                    
                    # 如果没有review，创建默认的
                    if not review:
                        logger.info(f"为内容 {content.id} 创建默认预审记录")
                        review = await CRUD.create_review(
                            session=session,
                            content_id=content.id,
                            novelty_score=60,
                            utility_score=60,
                            authority_score=60,
                            timeliness_score=60,
                            completeness_score=60,
                            total_score=60.0,
                            passed=True,
                            review_notes="系统自动修复创建的默认预审记录",
                        )
                    
                    # 创建学习记录
                    await CRUD.create_learning_record(
                        session=session,
                        content=content,
                        review=review,
                        analysis=analysis,
                    )
                    fixed_count += 1
                    logger.info(f"为内容 {content.id} 创建了学习记录")
                except Exception as e:
                    logger.error(f"处理内容 {content.id} 时出错: {e}")
                    errors.append(f"内容 {content.title[:30]}: {str(e)}")
            
            # 2. 清理孤立的学习记录（对应内容不存在或状态不是analyzed）
            lr_result = await session.execute(select(LearningRecord))
            all_records = list(lr_result.scalars().all())
            logger.info(f"找到 {len(all_records)} 条学习记录")
            
            records_to_delete = []
            for record in all_records:
                try:
                    content_result = await session.execute(
                        select(Content).where(Content.id == record.content_id)
                    )
                    content = content_result.scalar_one_or_none()
                    
                    if not content or content.status != "analyzed":
                        records_to_delete.append(record)
                except Exception as e:
                    logger.error(f"检查学习记录 {record.id} 时出错: {e}")
            
            # 批量删除孤立记录
            for record in records_to_delete:
                try:
                    await session.delete(record)
                    deleted_count += 1
                    logger.info(f"删除孤立记录: {record.title[:30]}")
                except Exception as e:
                    logger.error(f"删除记录 {record.id} 时出错: {e}")
                    errors.append(f"删除失败: {record.title[:30]}")
            
            if records_to_delete:
                await session.commit()
        
        return BaseResponse(
            message=f"数据一致性修复完成：创建 {fixed_count} 条，删除 {deleted_count} 条孤立记录",
            data={"fixed_count": fixed_count, "deleted_count": deleted_count, "errors": errors}
        )
    except Exception as e:
        logger.error(f"fix_data_consistency 出错: {e}", exc_info=True)
        return BaseResponse(
            success=False,
            message=f"修复失败: {str(e)}",
            data={"errors": [str(e)]}
        )


@router.get("/check-consistency")
async def check_data_consistency():
    """检查数据一致性"""
    try:
        async with db.async_session() as session:
            # 统计已分析内容数量
            analyzed_result = await session.execute(
                select(func.count()).select_from(Content).where(Content.status == "analyzed")
            )
            analyzed_count = analyzed_result.scalar() or 0
            
            # 统计学习记录数量
            lr_result = await session.execute(
                select(func.count()).select_from(LearningRecord)
            )
            lr_count = lr_result.scalar() or 0
            
            # 查找缺失学习记录的内容
            missing_result = await session.execute(
                select(Content).where(Content.status == "analyzed")
            )
            analyzed_contents = list(missing_result.scalars().all())
            
            missing_learning_records = []
            for content in analyzed_contents:
                lr_check = await session.execute(
                    select(LearningRecord).where(LearningRecord.content_id == content.id)
                )
                if not lr_check.scalar_one_or_none():
                    missing_learning_records.append({
                        "id": content.id,
                        "title": content.title[:50] if len(content.title) > 50 else content.title,
                    })
            
            # 查找孤立的学习记录
            orphan_result = await session.execute(select(LearningRecord))
            all_records = list(orphan_result.scalars().all())
            
            orphan_records = []
            for record in all_records:
                content_check = await session.execute(
                    select(Content).where(Content.id == record.content_id)
                )
                content = content_check.scalar_one_or_none()
                if not content or content.status != "analyzed":
                    orphan_records.append({
                        "id": record.id,
                        "title": record.title[:50] if len(record.title) > 50 else record.title,
                        "content_status": content.status if content else "deleted",
                    })
            
            return {
                "analyzed_content_count": analyzed_count,
                "learning_record_count": lr_count,
                "missing_learning_records": missing_learning_records,
                "orphan_learning_records": orphan_records,
                "is_consistent": len(missing_learning_records) == 0 and len(orphan_records) == 0,
            }
    except Exception as e:
        logger.error(f"check_data_consistency 出错: {e}", exc_info=True)
        return {
            "analyzed_content_count": 0,
            "learning_record_count": 0,
            "missing_learning_records": [],
            "orphan_learning_records": [],
            "is_consistent": True,
            "error": str(e),
        }
