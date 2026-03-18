"""系统设置路由"""
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/settings", tags=["系统设置"])


class EnvConfig(BaseModel):
    """环境变量配置"""
    openai_api_key: Optional[str] = None
    openai_api_base: Optional[str] = None
    model_name: Optional[str] = None
    model_temperature: Optional[float] = None
    passing_score: Optional[int] = None
    collect_interval_hours: Optional[int] = None


@router.get("")
async def get_settings():
    """获取系统设置"""
    # 获取数据库类型
    db_type = "SQLite"
    if "postgresql" in settings.database_url:
        db_type = "PostgreSQL"
    
    # 获取LLM配置详情
    llm_config = None
    if settings.openai_api_key:
        llm_config = {
            "provider": "OpenAI",
            "model": settings.model_name,
            "api_base": settings.openai_api_base,
            "temperature": settings.model_temperature,
            "configured": True,
        }
    elif settings.anthropic_api_key:
        llm_config = {
            "provider": "Anthropic",
            "model": "claude",
            "configured": True,
        }
    else:
        llm_config = {
            "provider": None,
            "model": None,
            "configured": False,
        }
    
    return {
        "app_name": "Metis",
        "version": settings.app_version,
        "debug": settings.debug,
        "log_level": settings.log_level,
        # 数据库信息
        "database": {
            "type": db_type,
            "connected": True,
            "url_display": _mask_db_url(settings.database_url),
        },
        # LLM配置
        "llm": llm_config,
        # 采集配置
        "collect_interval_hours": settings.collect_interval_hours,
        "max_items_per_run": settings.max_items_per_run,
        # 预审配置
        "passing_score": settings.passing_score,
    }


def _mask_db_url(url: str) -> str:
    """隐藏数据库URL中的敏感信息"""
    if "://" in url:
        # 只显示数据库类型和文件名
        parts = url.split("://")
        db_type = parts[0].split("+")[0]
        if "/" in parts[1]:
            db_name = parts[1].split("/")[-1]
            return f"{db_type}://{db_name}"
    return url


@router.get("/env")
async def get_env_config():
    """获取当前环境变量配置（敏感信息脱敏）"""
    return {
        "openai_api_key": _mask_api_key(settings.openai_api_key),
        "openai_api_base": settings.openai_api_base,
        "model_name": settings.model_name,
        "model_temperature": settings.model_temperature,
        "passing_score": settings.passing_score,
        "collect_interval_hours": settings.collect_interval_hours,
    }


def _mask_api_key(key: Optional[str]) -> str:
    """脱敏API Key"""
    if not key:
        return ""
    if len(key) <= 8:
        return "****"
    return key[:4] + "****" + key[-4:]


@router.post("/env")
async def update_env_config(config: EnvConfig):
    """更新环境变量配置到.env文件"""
    env_path = Path(".env")
    
    # 读取现有.env内容
    existing = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    existing[key.strip()] = value.strip()
    
    # 更新配置
    updates = {
        "OPENAI_API_KEY": config.openai_api_key,
        "OPENAI_API_BASE": config.openai_api_base,
        "MODEL_NAME": config.model_name,
        "MODEL_TEMPERATURE": str(config.model_temperature) if config.model_temperature is not None else None,
        "PASSING_SCORE": str(config.passing_score) if config.passing_score is not None else None,
        "COLLECT_INTERVAL_HOURS": str(config.collect_interval_hours) if config.collect_interval_hours is not None else None,
    }
    
    for key, value in updates.items():
        if value is not None:
            existing[key] = value
    
    # 写回.env文件
    with open(env_path, "w", encoding="utf-8") as f:
        for key, value in existing.items():
            # 如果值包含空格或特殊字符，用引号包裹
            if " " in str(value) or any(c in str(value) for c in ["#", "$"]):
                f.write(f'{key}="{value}"\n')
            else:
                f.write(f"{key}={value}\n")
    
    logger.info("环境变量配置已更新，需要重启服务生效")
    
    return {
        "success": True,
        "message": "配置已保存，请重启服务使配置生效",
    }


@router.post("/reload")
async def reload_config():
    """重载配置（需要重启服务）"""
    logger.info("收到重载配置请求")
    return {
        "success": True,
        "message": "请手动重启后端服务以加载新配置",
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
