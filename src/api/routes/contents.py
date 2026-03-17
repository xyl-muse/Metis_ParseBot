"""内容管理路由"""
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from src.api.schemas import (
    ContentListResponse,
    ContentResponse,
    BaseResponse,
)
from src.db.crud import CRUD, db
from src.db.models import Content
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/contents", tags=["内容管理"])


@router.get("/dashboard")
async def get_dashboard():
    """获取仪表盘统计数据"""
    import json
    from sqlalchemy import select, func
    from src.db.models import Content
    
    try:
        async with db.async_session() as session:
            # 统计各状态数量
            status_counts = {}
            for status in ["pending", "reviewed", "analyzed", "rejected"]:
                stmt = select(func.count()).select_from(Content).where(Content.status == status)
                result = await session.execute(stmt)
                status_counts[status] = result.scalar() or 0
            
            # 获取总数
            total_stmt = select(func.count()).select_from(Content)
            total_result = await session.execute(total_stmt)
            total = total_result.scalar() or 0
            
            logger.info(f"Dashboard stats: total={total}, status_counts={status_counts}")
            
            # 获取最近内容 - 按 collected_at 降序，如果为 NULL 则按 id 降序
            recent_stmt = (
                select(Content)
                .order_by(Content.collected_at.desc().nulls_last(), Content.id.desc())
                .limit(5)
            )
            recent_result = await session.execute(recent_stmt)
            recent_contents = recent_result.scalars().all()
            
            logger.info(f"Found {len(recent_contents)} recent contents")
            
            # 构建返回数据
            recent_data = []
            for c in recent_contents:
                try:
                    tags_data = json.loads(c.tags) if c.tags else None
                except (json.JSONDecodeError, TypeError):
                    tags_data = None
                
                recent_data.append({
                    "id": c.id,
                    "title": c.title or "无标题",
                    "source": c.source or "",
                    "source_url": c.source_url or "",
                    "category": c.category or "",
                    "summary": c.summary or "",
                    "status": c.status or "pending",
                    "tags": tags_data,
                    "collected_at": c.collected_at.isoformat() if c.collected_at else None,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                })
            
            response_data = {
                "total": total,
                "status_counts": status_counts,
                "recent_contents": recent_data
            }
            
            logger.info(f"Dashboard response: total={total}, recent_count={len(recent_data)}")
            
            return response_data
            
    except Exception as e:
        logger.error(f"Dashboard API error: {e}", exc_info=True)
        # 返回空数据而不是抛出错误
        return {
            "total": 0,
            "status_counts": {"pending": 0, "reviewed": 0, "analyzed": 0, "rejected": 0},
            "recent_contents": []
        }


async def get_session():
    """获取数据库会话"""
    async with db.async_session() as session:
        yield session


@router.get("", response_model=ContentListResponse)
async def list_contents(
    status: Optional[str] = Query(None, description="状态筛选"),
    category: Optional[str] = Query(None, description="分类筛选"),
    source: Optional[str] = Query(None, description="来源筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    session: AsyncSession = Depends(get_session),
):
    """获取内容列表"""
    offset = (page - 1) * page_size
    
    # 构建查询条件
    conditions = []
    if status:
        conditions.append(Content.status == status)
    if category:
        conditions.append(Content.category == category)
    if source:
        conditions.append(Content.source == source)
    
    # 获取总数
    count_stmt = select(func.count()).select_from(Content)
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    total_result = await session.execute(count_stmt)
    total = total_result.scalar() or 0
    
    # 获取数据
    contents = await CRUD.list_contents(
        session,
        status=status,
        category=category,
        source=source,
        limit=page_size,
        offset=offset,
    )
    
    # 转换为响应格式
    data = []
    for content in contents:
        data.append(ContentResponse(
            id=content.id,
            title=content.title,
            source=content.source,
            source_url=content.source_url,
            category=content.category,
            summary=content.summary,
            status=content.status,
            authors=json.loads(content.authors) if content.authors else None,
            tags=json.loads(content.tags) if content.tags else None,
            collected_at=content.collected_at,
            updated_at=content.updated_at,
        ))
    
    return ContentListResponse(
        data=data,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    session: AsyncSession = Depends(get_session),
):
    """获取单个内容详情"""
    content = await CRUD.get_content(session, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")
    
    import json
    return ContentResponse(
        id=content.id,
        title=content.title,
        source=content.source,
        source_url=content.source_url,
        category=content.category,
        summary=content.summary,
        status=content.status,
        authors=json.loads(content.authors) if content.authors else None,
        tags=json.loads(content.tags) if content.tags else None,
        collected_at=content.collected_at,
        updated_at=content.updated_at,
    )


@router.delete("/{content_id}", response_model=BaseResponse)
async def delete_content(
    content_id: str,
    session: AsyncSession = Depends(get_session),
):
    """删除内容"""
    content = await CRUD.get_content(session, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")
    
    await session.delete(content)
    await session.commit()
    
    return BaseResponse(message="删除成功")
