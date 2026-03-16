"""任务调度服务"""
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.core.config import settings
from src.core.logging import get_logger, setup_logging
from src.services.pipeline import pipeline

logger = get_logger(__name__)


class Scheduler:
    """任务调度器"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._started = False

    def start(self) -> None:
        """启动调度器"""
        if self._started:
            logger.warning("调度器已经启动")
            return

        # 添加定时采集任务
        self.scheduler.add_job(
            self._scheduled_collect,
            IntervalTrigger(hours=settings.collect_interval_hours),
            id="scheduled_collect",
            name="定时采集任务",
            replace_existing=True,
        )

        self.scheduler.start()
        self._started = True
        logger.info(f"调度器已启动，采集间隔: {settings.collect_interval_hours} 小时")

    def stop(self) -> None:
        """停止调度器"""
        if self._started:
            self.scheduler.shutdown()
            self._started = False
            logger.info("调度器已停止")

    async def _scheduled_collect(self) -> None:
        """定时采集任务"""
        logger.info(f"开始执行定时采集任务: {datetime.now()}")
        try:
            result = await pipeline.run(
                collect=True,
                review=True,
                analyze=True,
                limit=settings.max_items_per_run,
            )
            logger.info(f"定时采集任务完成: {result}")
        except Exception as e:
            logger.error(f"定时采集任务失败: {e}")

    def get_jobs(self) -> list[dict]:
        """获取所有任务状态"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            })
        return jobs


# 导出实例
scheduler = Scheduler()
