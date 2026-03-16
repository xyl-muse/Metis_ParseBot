"""预审路由"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    ReviewRequest,
    ReviewResponse,
    ReviewListResponse,
    ScoreDetail,
    BaseResponse,
)
from src.agents.reviewer.agent import ReviewerAgent
from src.db.crud import CRUD, db
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/review", tags=["预审管理"])


async def get_session():
    """获取数据库会话"""
    async with db.async_session() as session:
        yield session


@router.post("", response_model=BaseResponse)
async def trigger_review(
    request: Optional[ReviewRequest] = None,
    limit: int = Query(50, ge=1, le=100, description="最大处理数量"),
    session: AsyncSession = Depends(get_session),
):
    """触发预审任务"""
    logger.info(f"触发预审任务: content_id={request.content_id if request else None}")
    
    agent = ReviewerAgent()
    result = await agent.run(
        content_id=request.content_id if request else None,
        session=session,
        limit=limit,
    )
    
    return BaseResponse(
        message=f"预审完成: 处理 {result['total_processed']}, 通过 {result['passed']}, 拒绝 {result['rejected']}"
    )


@router.get("/pending")
async def get_pending_contents(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """获取待预审内容列表"""
    contents = await CRUD.list_contents(session, status="pending", limit=limit)
    return {
        "data": [
            {
                "id": c.id,
                "title": c.title,
                "source": c.source,
                "category": c.category,
                "collected_at": c.collected_at.isoformat(),
            }
            for c in contents
        ],
        "total": len(contents),
    }


@router.get("/passed")
async def get_passed_contents(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """获取通过预审的内容列表（按分数降序）"""
    agent = ReviewerAgent()
    contents = await agent.get_passed_contents(session, limit=limit)
    
    result_data = []
    for content in contents:
        review = await CRUD.get_review_by_content(session, content.id)
        result_data.append({
            "content_id": content.id,
            "title": content.title,
            "source": content.source,
            "category": content.category,
            "total_score": review.total_score if review else 0,
        })
    
    return {
        "data": result_data,
        "total": len(result_data),
    }


@router.get("/{content_id}", response_model=ReviewResponse)
async def get_review(
    content_id: str,
    session: AsyncSession = Depends(get_session),
):
    """获取内容的预审结果"""
    review = await CRUD.get_review_by_content(session, content_id)
    if not review:
        raise HTTPException(status_code=404, detail="预审记录不存在")
    
    return ReviewResponse(
        id=review.id,
        content_id=review.content_id,
        total_score=review.total_score,
        passed=review.passed,
        score_detail=ScoreDetail(
            novelty_score=review.novelty_score,
            utility_score=review.utility_score,
            authority_score=review.authority_score,
            timeliness_score=review.timeliness_score,
            completeness_score=review.completeness_score,
        ),
        review_notes=review.review_notes,
        reviewed_at=review.reviewed_at,
    )
