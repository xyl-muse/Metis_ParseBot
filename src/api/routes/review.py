"""预审路由"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
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

# 全局预审智能体实例（用于查询进度）
_reviewer_agent: Optional[ReviewerAgent] = None
_review_progress: dict = {
    "status": "idle",
    "total": 0,
    "processed": 0,
    "passed": 0,
    "rejected": 0,
    "current_item": None,
}


async def get_session():
    """获取数据库会话"""
    async with db.async_session() as session:
        yield session


async def run_review_background(content_id: Optional[str], limit: int):
    """后台执行预审任务"""
    global _review_progress, _reviewer_agent
    
    _review_progress = {"status": "running", "total": 0, "processed": 0, "passed": 0, "rejected": 0, "current_item": None}
    
    try:
        async with db.async_session() as session:
            # 传入全局进度字典，让agent直接更新
            _reviewer_agent = ReviewerAgent(progress_dict=_review_progress)
            result = await _reviewer_agent.run(
                content_id=content_id,
                session=session,
                limit=limit,
            )
            _review_progress["status"] = "completed"
            logger.info(f"后台预审完成: {result}")
    except Exception as e:
        logger.error(f"后台预审失败: {e}")
        _review_progress["status"] = "error"
        _review_progress["error"] = str(e)


@router.post("", response_model=BaseResponse)
async def trigger_review(
    background_tasks: BackgroundTasks,
    request: Optional[ReviewRequest] = None,
    limit: int = Query(50, ge=1, le=100, description="最大处理数量"),
    session: AsyncSession = Depends(get_session),
):
    """触发预审任务（后台执行）"""
    global _review_progress
    
    if _review_progress.get("status") == "running":
        return BaseResponse(success=False, message="已有预审任务正在执行中")
    
    content_id = request.content_id if request else None
    logger.info(f"触发预审任务: content_id={content_id}")
    
    # 重置进度
    _review_progress = {"status": "starting", "total": 0, "processed": 0, "passed": 0, "rejected": 0, "current_item": None}
    
    # 启动后台任务
    background_tasks.add_task(run_review_background, content_id, limit)
    
    return BaseResponse(message="预审任务已启动，请通过进度API查询进度")


@router.get("/progress")
async def get_review_progress():
    """获取预审进度"""
    global _review_progress, _reviewer_agent
    
    # 优先使用全局进度（后台任务模式）
    if _review_progress.get("status") != "idle":
        progress = _review_progress
        return {
            "status": progress.get("status", "idle"),
            "total": progress.get("total", 0),
            "processed": progress.get("processed", 0),
            "passed": progress.get("passed", 0),
            "rejected": progress.get("rejected", 0),
            "current_item": progress.get("current_item"),
            "percentage": round(progress.get("processed", 0) / max(progress.get("total", 1), 1) * 100, 1),
        }
    
    # 兼容模式：从agent获取进度
    if _reviewer_agent is None:
        return {
            "status": "idle",
            "total": 0,
            "processed": 0,
            "passed": 0,
            "rejected": 0,
            "current_item": None,
            "percentage": 0,
        }
    
    progress = _reviewer_agent.get_progress()
    return {
        "status": progress.get("status", "idle"),
        "total": progress.get("total", 0),
        "processed": progress.get("processed", 0),
        "passed": progress.get("passed", 0),
        "rejected": progress.get("rejected", 0),
        "current_item": progress.get("current_item"),
        "percentage": round(progress.get("processed", 0) / max(progress.get("total", 1), 1) * 100, 1),
    }


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
