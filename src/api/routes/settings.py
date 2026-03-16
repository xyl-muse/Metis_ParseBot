"""系统设置路由"""
from fastapi import APIRouter

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/settings", tags=["系统设置"])


@router.get("")
async def get_settings():
    """获取系统设置"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "model_name": settings.model_name,
        "model_temperature": settings.model_temperature,
        "max_tokens": settings.max_tokens,
        "collect_interval_hours": settings.collect_interval_hours,
        "max_items_per_run": settings.max_items_per_run,
        "passing_score": settings.passing_score,
        "arxiv_categories": settings.arxiv_categories,
        "news_sources": settings.news_sources,
        "llm_provider": settings.get_llm_provider() if settings.openai_api_key else None,
    }


@router.get("/sources")
async def get_sources():
    """获取数据源配置"""
    return {
        "arxiv": {
            "name": "arXiv",
            "type": "academic",
            "categories": settings.arxiv_categories,
            "max_results": settings.arxiv_max_results,
            "enabled": True,
        },
        "hackernews": {
            "name": "Hacker News",
            "type": "news",
            "enabled": "hackernews" in settings.news_sources,
        },
        "reddit_ml": {
            "name": "Reddit MachineLearning",
            "type": "news",
            "enabled": "reddit_ml" in settings.news_sources,
        },
        "reddit_security": {
            "name": "Reddit netsec",
            "type": "news",
            "enabled": "reddit_security" in settings.news_sources,
        },
    }


@router.post("/scheduler/start")
async def start_scheduler():
    """启动定时调度器"""
    from src.services.scheduler import scheduler
    
    if scheduler.is_running:
        return {"status": "already_running", "message": "调度器已在运行"}
    
    scheduler.start()
    return {"status": "started", "message": "调度器已启动"}


@router.post("/scheduler/stop")
async def stop_scheduler():
    """停止定时调度器"""
    from src.services.scheduler import scheduler
    
    if not scheduler.is_running:
        return {"status": "already_stopped", "message": "调度器已停止"}
    
    scheduler.stop()
    return {"status": "stopped", "message": "调度器已停止"}


@router.get("/scheduler/status")
async def get_scheduler_status():
    """获取调度器状态"""
    from src.services.scheduler import scheduler
    
    return {
        "is_running": scheduler.is_running,
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None,
            }
            for job in scheduler.get_jobs()
        ]
    }
