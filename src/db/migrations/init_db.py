"""数据库初始化脚本"""
import asyncio

from src.core.logging import setup_logging, get_logger
from src.db.crud import db

logger = get_logger(__name__)


async def init_database() -> None:
    """初始化数据库"""
    logger.info("开始初始化数据库...")
    await db.create_tables()
    logger.info("数据库初始化完成")


async def main() -> None:
    """主函数"""
    setup_logging(log_level="INFO")
    await init_database()


if __name__ == "__main__":
    asyncio.run(main())
