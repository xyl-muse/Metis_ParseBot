"""分析路由"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
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


async def get_session():
    """获取数据库会话"""
    async with db.async_session() as session:
        yield session


@router.post("", response_model=BaseResponse)
async def trigger_analyze(
    request: Optional[AnalysisRequest] = None,
    limit: int = Query(50, ge=1, le=100, description="最大处理数量"),
    session: AsyncSession = Depends(get_session),
):
    """触发分析任务"""
    logger.info(f"触发分析任务: content_id={request.content_id if request else None}")
    
    agent = AnalyzerAgent()
    result = await agent.run(
        content_id=request.content_id if request else None,
        session=session,
        limit=limit,
    )
    
    return BaseResponse(
        message=f"分析完成: 处理 {result['total_processed']}, 成功 {result['success']}"
    )


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
