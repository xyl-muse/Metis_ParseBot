"""新闻数据源适配器"""
from datetime import datetime, timezone
from typing import Optional
import json

import httpx

from src.agents.collector.sources.base import BaseSource, CollectedItem
from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import SourceConnectionError, SourceTimeoutError

logger = get_logger(__name__)


class HackerNewsSource(BaseSource):
    """Hacker News 数据源"""

    def __init__(self, timeout: int = 30):
        super().__init__(name="hackernews", timeout=timeout)
        self.base_url = "https://hacker-news.firebaseio.com/v0"

    async def fetch(self, limit: int = 20) -> list[CollectedItem]:
        """获取 HN 顶部故事"""
        items = []
        timeout = self.config.get("timeout", 30)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                # 获取顶部故事 ID
                response = await client.get(f"{self.base_url}/topstories.json")
                response.raise_for_status()
                story_ids = response.json()[:limit]
                
                # 获取每个故事的详情
                for story_id in story_ids:
                    try:
                        story_response = await client.get(
                            f"{self.base_url}/item/{story_id}.json"
                        )
                        story_response.raise_for_status()
                        story = story_response.json()
                        
                        if story and story.get("url"):
                            item = self._parse_story(story)
                            items.append(item)
                            
                    except Exception as e:
                        logger.warning(f"[HN] 获取故事 {story_id} 失败: {e}")
                        continue
                        
            except httpx.TimeoutException:
                raise SourceTimeoutError("Hacker News 请求超时")
            except Exception as e:
                raise SourceConnectionError(f"Hacker News 连接失败: {e}")

        logger.info(f"[HN] 成功获取 {len(items)} 条新闻")
        return items

    def _parse_story(self, story: dict) -> CollectedItem:
        """解析 HN 故事"""
        published_date = None
        if story.get("time"):
            published_date = datetime.fromtimestamp(story["time"], tz=timezone.utc)

        return CollectedItem(
            title=story.get("title", ""),
            source="hackernews",
            source_url=story.get("url", f"https://news.ycombinator.com/item?id={story.get('id')}"),
            category="news_ai",  # 需要后续通过 LLM 分类
            raw_content=story.get("text"),
            summary=story.get("title"),
            authors=[story.get("by")] if story.get("by") else None,
            published_date=published_date,
            tags=["hackernews"],
            metadata={
                "hn_id": story.get("id"),
                "score": story.get("score"),
                "descendants": story.get("descendants"),
            },
        )


class RedditSource(BaseSource):
    """Reddit 数据源"""

    # 订阅版块配置
    SUBREDDIT_CONFIG = {
        "reddit_ml": {
            "subreddit": "MachineLearning",
            "category": "news_ai",
        },
        "reddit_security": {
            "subreddit": "netsec",
            "category": "news_security",
        },
        "reddit_ai": {
            "subreddit": "artificial",
            "category": "news_ai",
        },
    }

    def __init__(self, subreddit_type: str = "reddit_ml", timeout: int = 30):
        super().__init__(name=subreddit_type, timeout=timeout)
        self.subreddit_type = subreddit_type
        self.base_url = "https://www.reddit.com"

    async def fetch(self, limit: int = 20) -> list[CollectedItem]:
        """获取 Reddit 热门帖子"""
        items = []
        timeout = self.config.get("timeout", 30)
        
        config = self.SUBREDDIT_CONFIG.get(self.subreddit_type, self.SUBREDDIT_CONFIG["reddit_ml"])
        subreddit = config["subreddit"]
        default_category = config["category"]
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                url = f"{self.base_url}/r/{subreddit}/hot.json?limit={limit}"
                headers = {"User-Agent": "Metis_ParseBot/0.1.0"}
                
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                for child in data.get("data", {}).get("children", []):
                    post = child.get("data", {})
                    if post and post.get("url"):
                        item = self._parse_post(post, default_category)
                        items.append(item)
                        
            except httpx.TimeoutException:
                raise SourceTimeoutError(f"Reddit {subreddit} 请求超时")
            except Exception as e:
                raise SourceConnectionError(f"Reddit {subreddit} 连接失败: {e}")

        logger.info(f"[Reddit/{subreddit}] 成功获取 {len(items)} 条帖子")
        return items

    def _parse_post(self, post: dict, default_category: str) -> CollectedItem:
        """解析 Reddit 帖子"""
        published_date = None
        if post.get("created_utc"):
            published_date = datetime.fromtimestamp(post["created_utc"], tz=timezone.utc)

        # 使用 Reddit 自带链接或外部链接
        url = post.get("url")
        if url.startswith("/r/"):
            url = f"{self.base_url}{url}"

        return CollectedItem(
            title=post.get("title", ""),
            source=self.subreddit_type,
            source_url=url,
            category=default_category,
            raw_content=post.get("selftext"),
            summary=post.get("title"),
            authors=[post.get("author")] if post.get("author") else None,
            published_date=published_date,
            tags=[post.get("subreddit"), "reddit"],
            metadata={
                "reddit_id": post.get("id"),
                "score": post.get("score"),
                "num_comments": post.get("num_comments"),
                "permalink": post.get("permalink"),
            },
        )


class NewsSourceFactory:
    """新闻源工厂"""

    @staticmethod
    def create(source_name: str) -> BaseSource:
        """创建新闻源实例"""
        if source_name == "hackernews":
            return HackerNewsSource()
        elif source_name.startswith("reddit_"):
            return RedditSource(subreddit_type=source_name)
        else:
            raise ValueError(f"未知的新闻源: {source_name}")
