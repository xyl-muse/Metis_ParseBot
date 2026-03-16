"""FastAPI 应用主入口"""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.logging import setup_logging, get_logger
from src.core.exceptions import MetisError
from src.db.crud import db
from src.api.schemas import SystemStatusResponse, SystemStatus, PipelineResponse, PipelineResult, PipelineRequest
from src.api.routes import collect, review, analyze, learning
from src.api.routes.contents import router as contents_router
from src.api.routes.settings import router as settings_router
from src.services.pipeline import pipeline
from src.services.scheduler import scheduler

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    setup_logging(log_level=settings.log_level)
    logger.info(f"启动 {settings.app_name} v{settings.app_version}")
    
    # 初始化数据库
    await db.create_tables()
    logger.info("数据库初始化完成")
    
    # 启动调度器（可选）
    # scheduler.start()
    
    yield
    
    # 关闭时
    scheduler.stop()
    logger.info("应用关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="智能知识采集与分析系统 - 多智能体协作的AI知识学习助手",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 异常处理
@app.exception_handler(MetisError)
async def metis_exception_handler(request: Request, exc: MetisError):
    """处理自定义异常"""
    logger.error(f"MetisError: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理通用异常"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "detail": str(exc) if settings.debug else None,
        },
    )


# 注册路由
app.include_router(contents_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(collect.router, prefix="/api")
app.include_router(review.router, prefix="/api")
app.include_router(analyze.router, prefix="/api")
app.include_router(learning.router, prefix="/api")


# 根路由
@app.get("/", response_model=SystemStatusResponse)
async def root():
    """根路由 - 系统状态"""
    return SystemStatusResponse(
        data=SystemStatus(
            app_name=settings.app_name,
            version=settings.app_version,
            status="running",
            database_connected=True,
            llm_configured=bool(settings.openai_api_key or settings.anthropic_api_key),
        )
    )


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/status", response_model=SystemStatusResponse)
async def get_status():
    """获取系统状态"""
    return SystemStatusResponse(
        data=SystemStatus(
            app_name=settings.app_name,
            version=settings.app_version,
            status="running",
            database_connected=True,
            llm_configured=bool(settings.openai_api_key or settings.anthropic_api_key),
        )
    )


# 流水线路由
@app.post("/api/pipeline", response_model=PipelineResponse)
async def run_pipeline(request: PipelineRequest = PipelineRequest()):
    """执行完整流水线"""
    logger.info("执行完整流水线...")
    result = await pipeline.run(
        collect=request.collect,
        review=request.review,
        analyze=request.analyze,
        limit=request.limit,
    )
    
    return PipelineResponse(
        data=PipelineResult(
            collect=result["collect"],
            review=result["review"],
            analyze=result["analyze"],
        )
    )


# 调度器路由
@app.get("/api/scheduler/jobs")
async def get_scheduler_jobs():
    """获取调度任务列表"""
    return {
        "jobs": scheduler.get_jobs(),
        "is_running": scheduler._started,
    }


@app.post("/api/scheduler/start")
async def start_scheduler():
    """启动调度器"""
    scheduler.start()
    return {"message": "调度器已启动"}


@app.post("/api/scheduler/stop")
async def stop_scheduler():
    """停止调度器"""
    scheduler.stop()
    return {"message": "调度器已停止"}


def main():
    """应用入口"""
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=settings.api_workers,
    )


if __name__ == "__main__":
    main()
