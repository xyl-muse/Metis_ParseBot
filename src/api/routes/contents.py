"""内容管理路由"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    ContentListResponse,
    ContentResponse,
    BaseResponse,
)
from src.db.crud import CRUD, db
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/contents", tags=["内容管理"])


@router.get("/dashboard")
async def get_dashboard():
    """获取仪表盘统计数据"""
    async with db.async_session() as session:
        # 获取各状态内容数量
        from sqlalchemy import select, func
        from src.db.models import Content
        
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
        
        # 获取最近内容
        recent_stmt = select(Content).order_by(Content.collected_at.desc()).limit(5)
        recent_result = await session.execute(recent_stmt)
        recent_contents = recent_result.scalars().all()
        
        return {
            "total": total,
            "status_counts": status_counts,
            "recent_contents": [
                {
                    "id": c.id,
                    "title": c.title,
                    "source": c.source,
                    "category": c.category,
                    "status": c.status,
                    "collected_at": c.collected_at.isoformat() if c.collected_at else None,
                }
                for c in recent_contents
            ]
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
        import json
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
        total=len(data),  # 简化处理，实际应该单独查询总数
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
