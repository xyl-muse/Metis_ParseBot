"""采集路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import CollectRequest, CollectResponse, CollectResult
from src.agents.collector.agent import CollectorAgent
from src.db.crud import db
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/collect", tags=["采集管理"])


async def get_session():
    """获取数据库会话"""
    async with db.async_session() as session:
        yield session


@router.post("", response_model=CollectResponse)
async def trigger_collect(
    request: CollectRequest = CollectRequest(),
    session: AsyncSession = Depends(get_session),
):
    """触发采集任务"""
    logger.info(f"触发采集任务: sources={request.sources}, limit={request.limit_per_source}")
    
    agent = CollectorAgent()
    result = await agent.run(
        source_names=request.sources,
        limit_per_source=request.limit_per_source,
        session=session,
    )
    
    return CollectResponse(
        data=CollectResult(
            total_found=result["total_found"],
            total_collected=result["total_collected"],
            total_deduplicated=result["total_deduplicated"],
            by_source=result["by_source"],
            errors=result["errors"],
        )
    )


@router.get("/sources")
async def list_sources():
    """获取可用的数据源列表"""
    return {
        "sources": [
            {
                "name": "arxiv",
                "type": "academic",
                "description": "arXiv 学术论文",
                "categories": ["cs.AI", "cs.CL", "cs.LG", "cs.CR", "cs.CV"],
            },
            {
                "name": "hackernews",
                "type": "news",
                "description": "Hacker News 科技新闻",
            },
            {
                "name": "reddit_ml",
                "type": "news",
                "description": "Reddit MachineLearning 板块",
            },
            {
                "name": "reddit_security",
                "type": "news",
                "description": "Reddit netsec 板块",
            },
        ]
    }
