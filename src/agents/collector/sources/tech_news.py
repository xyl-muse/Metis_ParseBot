"""技术新闻数据源适配器"""
from datetime import datetime, timezone
from typing import Optional
import re
import asyncio

import httpx
from bs4 import BeautifulSoup

from src.agents.collector.sources.base import BaseSource, CollectedItem
from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import SourceConnectionError, SourceTimeoutError

logger = get_logger(__name__)


class GitHubTrendingSource(BaseSource):
    """GitHub Trending 数据源"""

    # AI/安全相关的语言和主题
    LANGUAGES = ["python", "jupyter-notebook", "rust", "go"]
    TOPICS = ["machine-learning", "deep-learning", "llm", "security", "cybersecurity"]

    def __init__(self, timeout: int = 30):
        super().__init__(name="github_trending", timeout=timeout)

    async def fetch(self, limit: int = 20) -> list[CollectedItem]:
        """获取 GitHub Trending 项目"""
        items = []
        timeout = self.config.get("timeout", 30)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                # 获取 AI 相关的 trending
                url = "https://github.com/trending"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/html,application/xhtml+xml",
                }
                
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                repos = soup.select("article.Box-row")
                
                for repo in repos[:limit]:
                    try:
                        item = self._parse_repo(repo)
                        if item and self._is_relevant(item.title, item.summary or ""):
                            items.append(item)
                    except Exception as e:
                        logger.debug(f"[GitHubTrending] 解析项目失败: {e}")
                        continue
                        
            except httpx.TimeoutException:
                raise SourceTimeoutError("GitHub Trending 请求超时")
            except Exception as e:
                raise SourceConnectionError(f"GitHub Trending 连接失败: {e}")

        logger.info(f"[GitHubTrending] 成功获取 {len(items)} 个项目")
        return items

    def _parse_repo(self, repo_element) -> Optional[CollectedItem]:
        """解析 GitHub 仓库"""
        try:
            # 获取仓库链接
            link = repo_element.select_one("h2 a")
            if not link:
                return None
                
            repo_path = link.get("href", "").strip()
            title = repo_path.lstrip("/")
            source_url = f"https://github.com{repo_path}"
            
            # 获取描述
            desc_element = repo_element.select_one("p.col-9")
            description = desc_element.get_text(strip=True) if desc_element else ""
            
            # 获取语言
            lang_element = repo_element.select_one("[itemprop='programmingLanguage']")
            language = lang_element.get_text(strip=True) if lang_element else ""
            
            # 获取星标数
            stars_element = repo_element.select_one("a[href$='/stargazers']")
            stars = 0
            if stars_element:
                stars_text = stars_element.get_text(strip=True)
                stars = self._parse_stars(stars_text)
            
            # 确定分类
            category = self._determine_category(title, description)
            
            return CollectedItem(
                title=title,
                source="github_trending",
                source_url=source_url,
                category=category,
                raw_content=description,
                summary=description or title,
                authors=None,
                published_date=datetime.now(timezone.utc),  # trending 没有明确的发布时间
                tags=["github", language, "trending"],
                metadata={
                    "language": language,
                    "stars": stars,
                    "repo_path": repo_path,
                },
            )
        except Exception as e:
            logger.debug(f"[GitHubTrending] 解析失败: {e}")
            return None

    def _parse_stars(self, stars_text: str) -> int:
        """解析星标数"""
        stars_text = stars_text.strip().lower().replace(",", "")
        if "k" in stars_text:
            return int(float(stars_text.replace("k", "")) * 1000)
        try:
            return int(stars_text)
        except:
            return 0

    def _is_relevant(self, title: str, description: str) -> bool:
        """检查是否与 AI/安全相关"""
        text = (title + " " + description).lower()
        
        ai_keywords = ["ai", "ml", "machine learning", "deep learning", "llm", 
                       "gpt", "transformer", "neural", "nlp", "cv", "computer vision",
                       "pytorch", "tensorflow", "langchain", "huggingface"]
        security_keywords = ["security", "security-tool", "penetration", "vulnerability",
                            "ctf", "exploit", "malware", "cryptography", "hack"]
        
        return any(kw in text for kw in ai_keywords + security_keywords)

    def _determine_category(self, title: str, description: str) -> str:
        """确定分类"""
        text = (title + " " + description).lower()
        
        security_keywords = ["security", "penetration", "vulnerability", "ctf", "exploit", "malware", "cryptography"]
        has_security = any(kw in text for kw in security_keywords)
        
        ai_keywords = ["ai", "ml", "machine learning", "deep learning", "llm", "gpt", "transformer", "neural"]
        has_ai = any(kw in text for kw in ai_keywords)
        
        if has_security and has_ai:
            return "news_cross"
        elif has_security:
            return "news_security"
        else:
            return "news_ai"


class HuggingFaceSource(BaseSource):
    """Hugging Face 模型/数据集数据源"""

    def __init__(self, timeout: int = 30):
        super().__init__(name="huggingface", timeout=timeout)
        self.base_url = "https://huggingface.co/api"

    async def fetch(self, limit: int = 20) -> list[CollectedItem]:
        """获取 Hugging Face 热门模型"""
        items = []
        timeout = self.config.get("timeout", 30)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                # 获取热门模型
                url = f"{self.base_url}/models"
                params = {
                    "sort": "downloads",
                    "direction": "-1",
                    "limit": limit,
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                models = response.json()
                
                for model in models[:limit]:
                    try:
                        item = self._parse_model(model)
                        if item:
                            items.append(item)
                    except Exception as e:
                        logger.debug(f"[HuggingFace] 解析模型失败: {e}")
                        continue
                        
            except httpx.TimeoutException:
                raise SourceTimeoutError("Hugging Face 请求超时")
            except Exception as e:
                raise SourceConnectionError(f"Hugging Face 连接失败: {e}")

        logger.info(f"[HuggingFace] 成功获取 {len(items)} 个模型")
        return items

    def _parse_model(self, model: dict) -> Optional[CollectedItem]:
        """解析模型数据"""
        model_id = model.get("modelId", "")
        if not model_id:
            return None
            
        title = model_id
        source_url = f"https://huggingface.co/{model_id}"
        
        # 获取描述
        description = model.get("description", "") or model.get("tags", [])
        if isinstance(description, list):
            description = " ".join(description)
        
        summary = description or f"Hugging Face 模型: {model_id}"
        
        # 确定分类
        tags = model.get("tags", [])
        category = self._determine_category(model_id, description, tags)
        
        # 下载量
        downloads = model.get("downloads", 0)
        
        return CollectedItem(
            title=title,
            source="huggingface",
            source_url=source_url,
            category=category,
            raw_content=description,
            summary=summary,
            authors=model.get("author", "").split("/") if model.get("author") else None,
            published_date=datetime.now(timezone.utc),
            tags=["huggingface"] + tags[:5],
            metadata={
                "model_id": model_id,
                "downloads": downloads,
                "tags": tags,
                "pipeline_tag": model.get("pipeline_tag"),
                "library_name": model.get("library_name"),
            },
        )

    def _determine_category(self, model_id: str, description: str, tags: list) -> str:
        """确定模型分类"""
        text = (model_id + " " + (description or "") + " " + " ".join(tags)).lower()
        
        security_keywords = ["security", "safety", "harmful", "jailbreak", "adversarial"]
        has_security = any(kw in text for kw in security_keywords)
        
        return "news_cross" if has_security else "news_ai"


class SecurityNewsSource(BaseSource):
    """安全新闻数据源 - 安全牛、FreeBuf 等"""

    SOURCES = {
        "freebuf": {
            "name": "FreeBuf",
            "rss_url": "https://www.freebuf.com/feed",
            "base_url": "https://www.freebuf.com",
        },
        "aqniu": {
            "name": "安全牛",
            "rss_url": "https://www.aqniu.com/feed",
            "base_url": "https://www.aqniu.com",
        },
    }

    def __init__(self, source_name: str = "freebuf", timeout: int = 30):
        super().__init__(name=f"security_{source_name}", timeout=timeout)
        self.source_key = source_name
        self.source_config = self.SOURCES.get(source_name, self.SOURCES["freebuf"])

    async def fetch(self, limit: int = 20) -> list[CollectedItem]:
        """获取安全新闻"""
        items = []
        timeout = self.config.get("timeout", 30)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                # 尝试获取 RSS
                rss_url = self.source_config["rss_url"]
                response = await client.get(rss_url)
                
                # 如果 RSS 不可用，尝试爬取主页
                if response.status_code != 200:
                    items = await self._fetch_from_homepage(client, limit)
                else:
                    items = self._parse_rss(response.text, limit)
                        
            except httpx.TimeoutException:
                raise SourceTimeoutError(f"{self.source_config['name']} 请求超时")
            except Exception as e:
                logger.warning(f"[{self.source_config['name']}] RSS 获取失败，尝试爬取: {e}")
                try:
                    items = await self._fetch_from_homepage(client, limit)
                except Exception as e2:
                    raise SourceConnectionError(f"{self.source_config['name']} 连接失败: {e2}")

        logger.info(f"[{self.source_config['name']}] 成功获取 {len(items)} 条新闻")
        return items

    def _parse_rss(self, rss_content: str, limit: int) -> list[CollectedItem]:
        """解析 RSS feed"""
        items = []
        
        try:
            soup = BeautifulSoup(rss_content, "xml")
            entries = soup.find_all("item")
            
            for entry in entries[:limit]:
                try:
                    title = entry.find("title").get_text(strip=True) if entry.find("title") else ""
                    link = entry.find("link").get_text(strip=True) if entry.find("link") else ""
                    description = entry.find("description").get_text(strip=True) if entry.find("description") else ""
                    pub_date = entry.find("pubDate").get_text(strip=True) if entry.find("pubDate") else None
                    
                    if not title or not link:
                        continue
                    
                    # 解析发布日期
                    published_date = None
                    if pub_date:
                        try:
                            published_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                        except:
                            try:
                                published_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S GMT")
                                published_date = published_date.replace(tzinfo=timezone.utc)
                            except:
                                pass
                    
                    # 确定分类
                    category = self._determine_category(title, description)
                    
                    items.append(CollectedItem(
                        title=title,
                        source=self.name,
                        source_url=link,
                        category=category,
                        raw_content=description,
                        summary=description or title,
                        authors=None,
                        published_date=published_date,
                        tags=[self.source_config["name"], "security"],
                        metadata={
                            "source": self.source_config["name"],
                        },
                    ))
                except Exception as e:
                    logger.debug(f"[{self.source_config['name']}] 解析 RSS 条目失败: {e}")
                    continue
        except Exception as e:
            logger.warning(f"[{self.source_config['name']}] RSS 解析失败: {e}")
            
        return items

    async def _fetch_from_homepage(self, client: httpx.AsyncClient, limit: int) -> list[CollectedItem]:
        """从主页爬取新闻"""
        items = []
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
        }
        
        response = await client.get(self.source_config["base_url"], headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 根据不同网站选择不同的选择器
        if self.source_key == "freebuf":
            articles = soup.select("div.news-info")
        else:
            articles = soup.select("article, .post, .news-item")
        
        for article in articles[:limit]:
            try:
                link_element = article.select_one("a[href]")
                title_element = article.select_one("h2, h3, .title")
                
                if not link_element or not title_element:
                    continue
                    
                title = title_element.get_text(strip=True)
                link = link_element.get("href", "")
                
                if not link.startswith("http"):
                    link = self.source_config["base_url"] + link
                
                description = article.get_text(strip=True)[:500]
                
                category = self._determine_category(title, description)
                
                items.append(CollectedItem(
                    title=title,
                    source=self.name,
                    source_url=link,
                    category=category,
                    raw_content=description,
                    summary=description or title,
                    authors=None,
                    published_date=datetime.now(timezone.utc),
                    tags=[self.source_config["name"], "security"],
                    metadata={"source": self.source_config["name"]},
                ))
            except Exception as e:
                logger.debug(f"[{self.source_config['name']}] 解析文章失败: {e}")
                continue
                
        return items

    def _determine_category(self, title: str, description: str) -> str:
        """确定新闻分类"""
        text = (title + " " + description).lower()
        
        ai_keywords = ["ai", "人工智能", "机器学习", "深度学习", "llm", "gpt", "模型"]
        has_ai = any(kw in text for kw in ai_keywords)
        
        return "news_cross" if has_ai else "news_security"


class AICompanyBlogSource(BaseSource):
    """AI 公司博客数据源"""

    # 公司博客 RSS 地址
    BLOGS = {
        "openai": {
            "name": "OpenAI",
            "url": "https://openai.com/blog",
            "rss": "https://openai.com/blog/rss.xml",
        },
        "anthropic": {
            "name": "Anthropic",
            "url": "https://www.anthropic.com/news",
            "rss": None,  # 可能没有 RSS
        },
        "deepmind": {
            "name": "DeepMind",
            "url": "https://deepmind.google/discover/blog/",
            "rss": None,
        },
        "google_ai": {
            "name": "Google AI",
            "url": "https://blog.google/technology/ai/",
            "rss": "https://blog.google/technology/ai/rss",
        },
    }

    def __init__(self, company: str = "openai", timeout: int = 30):
        super().__init__(name=f"blog_{company}", timeout=timeout)
        self.company = company
        self.blog_config = self.BLOGS.get(company, self.BLOGS["openai"])

    async def fetch(self, limit: int = 20) -> list[CollectedItem]:
        """获取公司博客文章"""
        items = []
        timeout = self.config.get("timeout", 30)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml",
                }
                
                if self.blog_config.get("rss"):
                    # 尝试 RSS
                    response = await client.get(self.blog_config["rss"], headers=headers)
                    if response.status_code == 200:
                        items = self._parse_rss(response.text, limit)
                
                if not items:
                    # 爬取主页
                    items = await self._fetch_from_homepage(client, limit)
                        
            except httpx.TimeoutException:
                raise SourceTimeoutError(f"{self.blog_config['name']} 请求超时")
            except Exception as e:
                raise SourceConnectionError(f"{self.blog_config['name']} 连接失败: {e}")

        logger.info(f"[{self.blog_config['name']}] 成功获取 {len(items)} 篇文章")
        return items

    def _parse_rss(self, rss_content: str, limit: int) -> list[CollectedItem]:
        """解析 RSS feed"""
        items = []
        
        try:
            soup = BeautifulSoup(rss_content, "xml")
            entries = soup.find_all("item")
            
            for entry in entries[:limit]:
                try:
                    title = entry.find("title").get_text(strip=True) if entry.find("title") else ""
                    link = entry.find("link").get_text(strip=True) if entry.find("link") else ""
                    description = entry.find("description").get_text(strip=True) if entry.find("description") else ""
                    
                    if not title or not link:
                        continue
                    
                    items.append(CollectedItem(
                        title=title,
                        source=self.name,
                        source_url=link,
                        category="news_ai",
                        raw_content=description,
                        summary=description or title,
                        authors=[self.blog_config["name"]],
                        published_date=datetime.now(timezone.utc),
                        tags=[self.blog_config["name"], "official-blog"],
                        metadata={"company": self.blog_config["name"]},
                    ))
                except Exception as e:
                    logger.debug(f"[{self.blog_config['name']}] 解析 RSS 条目失败: {e}")
                    continue
        except Exception as e:
            logger.warning(f"[{self.blog_config['name']}] RSS 解析失败: {e}")
            
        return items

    async def _fetch_from_homepage(self, client: httpx.AsyncClient, limit: int) -> list[CollectedItem]:
        """从主页爬取文章"""
        items = []
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
        }
        
        response = await client.get(self.blog_config["url"], headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 通用选择器
        articles = soup.select("article, .post, .blog-post, .card, [class*='article']")
        
        for article in articles[:limit]:
            try:
                link_element = article.select_one("a[href]")
                title_element = article.select_one("h1, h2, h3, .title, [class*='title']")
                
                if not link_element or not title_element:
                    continue
                    
                title = title_element.get_text(strip=True)
                link = link_element.get("href", "")
                
                if not link.startswith("http"):
                    from urllib.parse import urljoin
                    link = urljoin(self.blog_config["url"], link)
                
                description = article.get_text(strip=True)[:500]
                
                items.append(CollectedItem(
                    title=title,
                    source=self.name,
                    source_url=link,
                    category="news_ai",
                    raw_content=description,
                    summary=description or title,
                    authors=[self.blog_config["name"]],
                    published_date=datetime.now(timezone.utc),
                    tags=[self.blog_config["name"], "official-blog"],
                    metadata={"company": self.blog_config["name"]},
                ))
            except Exception as e:
                logger.debug(f"[{self.blog_config['name']}] 解析文章失败: {e}")
                continue
                
        return items
