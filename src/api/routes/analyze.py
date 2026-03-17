"""分析路由"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import json

from src.api.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisListResponse,
    KnowledgeLink,
    ConfusionNote,
    BaseResponse,
)
from src.agents.analyzer.agent import AnalyzerAgent
from src.db.crud import CRUD, db
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/analyze", tags=["分析管理"])

# 全局分析智能体实例（用于查询进度）
_analyzer_agent: Optional[AnalyzerAgent] = None
_analyze_progress: dict = {
    "status": "idle",
    "total": 0,
    "processed": 0,
    "success": 0,
    "failed": 0,
    "current_item": None,
}


async def get_session():
    """获取数据库会话"""
    async with db.async_session() as session:
        yield session


async def run_analyze_background(content_id: Optional[str], limit: int):
    """后台执行分析任务"""
    global _analyze_progress, _analyzer_agent
    
    _analyze_progress = {"status": "running", "total": 0, "processed": 0, "success": 0, "failed": 0, "current_item": None}
    
    try:
        async with db.async_session() as session:
            # 传入全局进度字典，让agent直接更新
            _analyzer_agent = AnalyzerAgent(progress_dict=_analyze_progress)
            result = await _analyzer_agent.run(
                content_id=content_id,
                session=session,
                limit=limit,
            )
            _analyze_progress["status"] = "completed"
            logger.info(f"后台分析完成: {result}")
    except Exception as e:
        logger.error(f"后台分析失败: {e}")
        _analyze_progress["status"] = "error"
        _analyze_progress["error"] = str(e)


@router.post("", response_model=BaseResponse)
async def trigger_analyze(
    background_tasks: BackgroundTasks,
    request: Optional[AnalysisRequest] = None,
    limit: int = Query(50, ge=1, le=100, description="最大处理数量"),
    session: AsyncSession = Depends(get_session),
):
    """触发分析任务（后台执行）"""
    global _analyze_progress
    
    if _analyze_progress.get("status") == "running":
        return BaseResponse(success=False, message="已有分析任务正在执行中")
    
    content_id = request.content_id if request else None
    logger.info(f"触发分析任务: content_id={content_id}")
    
    # 重置进度
    _analyze_progress = {"status": "starting", "total": 0, "processed": 0, "success": 0, "failed": 0, "current_item": None}
    
    # 启动后台任务
    background_tasks.add_task(run_analyze_background, content_id, limit)
    
    return BaseResponse(message="分析任务已启动，请通过进度API查询进度")


@router.get("/progress")
async def get_analyze_progress():
    """获取分析进度"""
    global _analyze_progress, _analyzer_agent
    
    # 优先使用全局进度（后台任务模式）
    if _analyze_progress.get("status") != "idle":
        progress = _analyze_progress
        return {
            "status": progress.get("status", "idle"),
            "total": progress.get("total", 0),
            "processed": progress.get("processed", 0),
            "success": progress.get("success", 0),
            "failed": progress.get("failed", 0),
            "current_item": progress.get("current_item"),
            "percentage": round(progress.get("processed", 0) / max(progress.get("total", 1), 1) * 100, 1),
        }
    
    # 兼容模式：从agent获取进度
    if _analyzer_agent is None:
        return {
            "status": "idle",
            "total": 0,
            "processed": 0,
            "success": 0,
            "failed": 0,
            "current_item": None,
            "percentage": 0,
        }
    
    progress = _analyzer_agent.get_progress()
    return {
        "status": progress.get("status", "idle"),
        "total": progress.get("total", 0),
        "processed": progress.get("processed", 0),
        "success": progress.get("success", 0),
        "failed": progress.get("failed", 0),
        "current_item": progress.get("current_item"),
        "percentage": round(progress.get("processed", 0) / max(progress.get("total", 1), 1) * 100, 1),
    }


@router.get("/analyzed")
async def get_analyzed_contents(
    category: Optional[str] = Query(None, description="分类筛选"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """获取已分析内容列表"""
    agent = AnalyzerAgent()
    contents = await agent.get_analyzed_contents(session, category=category, limit=limit)
    
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


@router.get("/{content_id}", response_model=AnalysisResponse)
async def get_analysis(
    content_id: str,
    session: AsyncSession = Depends(get_session),
):
    """获取内容的分析结果"""
    analysis = await CRUD.get_analysis_by_content(session, content_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="分析记录不存在")
    
    # 解析 JSON 字段
    key_points = json.loads(analysis.key_points) if analysis.key_points else []
    
    knowledge_links = None
    if analysis.knowledge_links:
        links_data = json.loads(analysis.knowledge_links)
        knowledge_links = [KnowledgeLink(**link) for link in links_data]
    
    confusion_notes = None
    if analysis.confusion_notes:
        notes_data = json.loads(analysis.confusion_notes)
        confusion_notes = [ConfusionNote(**note) for note in notes_data]
    
    related_topics = json.loads(analysis.related_topics) if analysis.related_topics else None
    
    return AnalysisResponse(
        id=analysis.id,
        content_id=analysis.content_id,
        summary=analysis.summary,
        key_points=key_points,
        knowledge_links=knowledge_links,
        confusion_notes=confusion_notes,
        learning_suggestions=analysis.learning_suggestions,
        related_topics=related_topics,
        analyzed_at=analysis.analyzed_at,
    )