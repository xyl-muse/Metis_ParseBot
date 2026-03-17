"""采集智能体"""
import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.base import BaseAgent
from src.agents.collector.sources.base import CollectedItem
from src.agents.collector.sources.arxiv import ArxivSource
from src.agents.collector.sources.news import NewsSourceFactory
from src.agents.collector.prompts import CLASSIFICATION_PROMPT
from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import CollectionError, ParseError
from src.db.crud import CRUD

logger = get_logger(__name__)


class CollectorAgent(BaseAgent):
    """
    采集智能体
    
    负责从多个数据源采集内容并进行初步分类。
    """

    def __init__(self, **kwargs):
        super().__init__(name="CollectorAgent", **kwargs)
        self._sources = self._init_sources()

    def _init_sources(self) -> dict:
        """初始化数据源"""
        sources = {}
        
        # 初始化 arXiv 源
        sources["arxiv"] = ArxivSource()
        
        # 初始化传统新闻源（HackerNews, Reddit）
        for news_source in settings.news_sources:
            try:
                sources[news_source] = NewsSourceFactory.create(news_source)
            except ValueError as e:
                logger.warning(f"初始化新闻源失败: {e}")
        
        # 初始化学术论文源
        for academic_source in settings.academic_sources:
            try:
                sources[academic_source] = NewsSourceFactory.create(academic_source)
            except ValueError as e:
                logger.warning(f"初始化学术源失败: {e}")
        
        # 初始化技术新闻源
        for tech_source in settings.tech_sources:
            try:
                sources[tech_source] = NewsSourceFactory.create(tech_source)
            except ValueError as e:
                logger.warning(f"初始化技术源失败: {e}")
        
        # 初始化安全新闻源
        for security_source in settings.security_sources:
            try:
                sources[security_source] = NewsSourceFactory.create(security_source)
            except ValueError as e:
                logger.warning(f"初始化安全源失败: {e}")
        
        # 初始化 AI 公司博客
        for blog_source in settings.ai_blog_sources:
            try:
                source_name = f"blog_{blog_source}"
                sources[source_name] = NewsSourceFactory.create(source_name)
            except ValueError as e:
                logger.warning(f"初始化博客源失败: {e}")
        
        logger.info(f"已初始化 {len(sources)} 个数据源: {list(sources.keys())}")
        
        return sources

    async def run(
        self,
        source_names: Optional[list[str]] = None,
        limit_per_source: Optional[int] = None,
        session: Optional[AsyncSession] = None,
    ) -> dict:
        """
        执行采集任务

        Args:
            source_names: 要采集的数据源列表，默认采集所有
            limit_per_source: 每个数据源的最大采集数量
            session: 数据库会话

        Returns:
            采集结果统计
        """
        limit = limit_per_source or settings.max_items_per_run
        sources_to_fetch = source_names or list(self._sources.keys())
        
        results = {
            "total_found": 0,
            "total_collected": 0,
            "total_deduplicated": 0,
            "by_source": {},
            "errors": [],
        }

        for source_name in sources_to_fetch:
            if source_name not in self._sources:
                logger.warning(f"未知的数据源: {source_name}")
                continue
            
            source = self._sources[source_name]
            try:
                logger.info(f"[{self.name}] 开始从 {source_name} 采集...")
                items = await source.fetch(limit=limit)
                
                results["total_found"] += len(items)
                results["by_source"][source_name] = {
                    "found": len(items),
                    "collected": 0,
                }

                # 处理每个采集项
                for item in items:
                    try:
                        processed = await self._process_item(item, session)
                        if processed:
                            results["total_collected"] += 1
                            results["by_source"][source_name]["collected"] += 1
                    except Exception as e:
                        logger.warning(f"[{self.name}] 处理内容失败: {item.title[:50]}, 错误: {e}")
                        results["errors"].append(str(e))

            except Exception as e:
                logger.error(f"[{self.name}] 采集 {source_name} 失败: {e}")
                results["errors"].append(f"{source_name}: {str(e)}")

        results["total_deduplicated"] = results["total_found"] - results["total_collected"]
        logger.info(
            f"[{self.name}] 采集完成: 发现 {results['total_found']}, "
            f"采集 {results['total_collected']}, 去重 {results['total_deduplicated']}"
        )

        return results

    async def _process_item(
        self,
        item: CollectedItem,
        session: Optional[AsyncSession] = None,
    ) -> bool:
        """
        处理单个采集项

        Args:
            item: 采集的内容项
            session: 数据库会话

        Returns:
            是否成功入库
        """
        if not session:
            return False

        # 检查内容时效性
        if not await self._check_content_timeliness(item):
            logger.debug(f"[{self.name}] 内容超过时效限制，跳过: {item.title[:50]}")
            return False

        # 检查是否已存在
        existing = await CRUD.get_content_by_url(session, item.source_url)
        if existing:
            logger.debug(f"[{self.name}] 内容已存在，跳过: {item.title[:50]}")
            return False

        # 使用 LLM 进行分类（如果需要）
        category = item.category
        if item.source in ["hackernews", "reddit_ml", "reddit_security"]:
            category = await self._classify_content(item)

        # 生成新的标签格式
        new_tags = self._generate_new_tags(item, category)
        
        # 合并原始标签和新生成的标签
        combined_tags = list(set(new_tags + (item.tags or [])))

        # 创建数据库记录
        await CRUD.create_content(
            session=session,
            title=item.title,
            source=item.source,
            source_url=item.source_url,
            category=category,
            raw_content=item.raw_content,
            summary=item.summary,
            authors=item.authors,
            published_date=item.published_date,
            tags=combined_tags,
        )

        logger.debug(f"[{self.name}] 成功入库: {item.title[:50]}")
        return True

    async def _check_content_timeliness(self, item: CollectedItem) -> bool:
        """
        检查内容时效性

        Args:
            item: 采集的内容项

        Returns:
            是否在时效范围内
        """
        # 如果没有发布时间，则默认通过检查
        if not item.published_date:
            return True

        # 获取当前时间（带时区）
        current_time = datetime.now(timezone.utc)
        
        # 确保 published_date 也是带时区的
        published_date = item.published_date
        if published_date.tzinfo is None:
            # 如果没有时区信息，假设为 UTC
            published_date = published_date.replace(tzinfo=timezone.utc)

        # 计算内容发布日期与当前日期的差值
        time_diff = current_time - published_date
        days_diff = time_diff.days

        # 检查是否超过配置的时效限制
        max_days = settings.content_age_limit_days
        if days_diff > max_days:
            logger.debug(f"[{self.name}] 内容已过期 ({days_diff}天前): {item.title[:50]}")
            return False

        return True

    async def _classify_content(self, item: CollectedItem) -> str:
        """
        使用 LLM 对内容进行分类

        Args:
            item: 待分类的内容项

        Returns:
            分类标签
        """
        try:
            prompt = CLASSIFICATION_PROMPT.format(
                title=item.title,
                summary=item.summary or item.title,
                source=item.source,
            )
            
            response = await self.invoke_llm(prompt)
            
            # 解析 JSON 响应
            try:
                # 尝试提取 JSON 部分
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    result = json.loads(json_str)
                    return result.get("category", "news_ai")
            except json.JSONDecodeError:
                pass
            
            # 默认分类
            return "news_ai"
            
        except Exception as e:
            logger.warning(f"[{self.name}] 分类失败，使用默认分类: {e}")
            return "news_ai"

    def _generate_new_tags(self, item: CollectedItem, category: str) -> list[str]:
        """
        根据新的"主题+分类"格式生成标签

        Args:
            item: 采集的内容项
            category: 原始分类

        Returns:
            新格式的标签列表
        """
        # 确定主题
        if "cross" in category:
            theme = "AI&安全"
        elif "ai" in category or "AI" in category:
            theme = "AI"
        elif "security" in category or "安全" in category or "CR" in category:
            theme = "安全"
        else:
            # 根据内容关键词判断
            title_lower = item.title.lower()
            summary_lower = (item.summary or "").lower()
            if any(keyword in title_lower or keyword in summary_lower 
                   for keyword in ["ai", "artificial intelligence", "machine learning", "deep learning", "llm", "gpt"]):
                theme = "AI"
            elif any(keyword in title_lower or keyword in summary_lower 
                     for keyword in ["security", "cyber", "cryptography", "vulnerability", "安全", "加密"]):
                theme = "安全"
            else:
                theme = "AI"  # 默认主题

        # 确定分类
        if "academic" in category or "学术" in category:
            classification = "学术"
        else:
            classification = "工程"
        
        # 生成标签
        tag = f"{theme}+{classification}"
        return [tag]

    async def collect_from_source(
        self,
        source_name: str,
        limit: int = 20,
    ) -> list[CollectedItem]:
        """
        从指定数据源采集内容（不入库）

        Args:
            source_name: 数据源名称
            limit: 最大数量

        Returns:
            采集的内容列表
        """
        if source_name not in self._sources:
            raise CollectionError(f"未知的数据源: {source_name}")

        return await self._sources[source_name].fetch(limit=limit)
