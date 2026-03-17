"""学术论文数据源适配器"""
from datetime import datetime, timezone
from typing import Optional
import asyncio

import httpx

from src.agents.collector.sources.base import BaseSource, CollectedItem
from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import SourceConnectionError, SourceTimeoutError

logger = get_logger(__name__)


class OpenReviewSource(BaseSource):
    """OpenReview 数据源 - AI/ML 顶会论文"""

    # 目标会议（CCF A/B 类）
    VENUES = [
        "ICLR", "NeurIPS", "ICML", "AAAI", "IJCAI",  # AI 顶会
        "CCS", "USENIX Security", "IEEE S&P", "NDSS",  # 安全顶会
    ]

    # AI/安全相关的关键词
    AI_KEYWORDS = [
        "machine learning", "deep learning", "neural network", 
        "large language model", "LLM", "GPT", "transformer",
        "reinforcement learning", "computer vision", "NLP",
        "generative AI", "diffusion model", "foundation model"
    ]
    
    SECURITY_KEYWORDS = [
        "security", "privacy", "adversarial", "attack", 
        "vulnerability", "cryptography", "authentication",
        "malware", "intrusion detection", "federated learning security"
    ]

    def __init__(self, timeout: int = 30):
        super().__init__(name="openreview", timeout=timeout)
        self.base_url = "https://api.openreview.net"

    async def fetch(self, limit: int = 20) -> list[CollectedItem]:
        """获取 OpenReview 最新论文"""
        items = []
        timeout = self.config.get("timeout", 30)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                # 获取最近的会议投稿
                for venue in self.VENUES[:3]:  # 先查询前几个会议
                    try:
                        venue_items = await self._fetch_venue(client, venue, limit // 3)
                        items.extend(venue_items)
                    except Exception as e:
                        logger.warning(f"[OpenReview] 获取 {venue} 失败: {e}")
                        continue
                    
                    # 添加延迟避免请求过快
                    await asyncio.sleep(0.5)
                    
            except httpx.TimeoutException:
                raise SourceTimeoutError("OpenReview 请求超时")
            except Exception as e:
                raise SourceConnectionError(f"OpenReview 连接失败: {e}")

        logger.info(f"[OpenReview] 成功获取 {len(items)} 篇论文")
        return items[:limit]

    async def _fetch_venue(
        self, 
        client: httpx.AsyncClient, 
        venue: str, 
        limit: int
    ) -> list[CollectedItem]:
        """获取特定会议的论文"""
        items = []
        
        try:
            # 查询会议的最新论文
            url = f"{self.base_url}/notes"
            params = {
                "content.venue": venue,
                "limit": limit,
                "details": "original,replies",
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for note in data.get("notes", []):
                try:
                    item = self._parse_note(note)
                    if item and self._is_relevant(item.title, item.summary or ""):
                        items.append(item)
                except Exception as e:
                    logger.debug(f"[OpenReview] 解析论文失败: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"[OpenReview] 获取 {venue} 失败: {e}")
            
        return items

    def _parse_note(self, note: dict) -> Optional[CollectedItem]:
        """解析 OpenReview 论文"""
        content = note.get("content", {})
        title = content.get("title", "")
        
        if not title:
            return None
            
        # 构建摘要
        abstract = content.get("abstract", "")
        tldr = content.get("TL;DR", "")
        summary = tldr or abstract or title
        
        # 确定分类
        category = self._determine_category(title, summary)
        
        # 构建链接
        forum_id = note.get("forum", note.get("id", ""))
        source_url = f"https://openreview.net/forum?id={forum_id}"
        
        # 发布日期
        cdate = note.get("cdate") or note.get("pdate")
        published_date = None
        if cdate:
            published_date = datetime.fromtimestamp(cdate / 1000, tz=timezone.utc)
        
        return CollectedItem(
            title=title,
            source="openreview",
            source_url=source_url,
            category=category,
            raw_content=abstract,
            summary=summary,
            authors=content.get("authors", []),
            published_date=published_date,
            tags=["openreview", content.get("venue", "")],
            metadata={
                "openreview_id": forum_id,
                "venue": content.get("venue"),
                "keywords": content.get("keywords", []),
            },
        )

    def _is_relevant(self, title: str, summary: str) -> bool:
        """检查内容是否与 AI/安全相关"""
        text = (title + " " + summary).lower()
        
        ai_match = any(kw.lower() in text for kw in self.AI_KEYWORDS)
        security_match = any(kw.lower() in text for kw in self.SECURITY_KEYWORDS)
        
        return ai_match or security_match

    def _determine_category(self, title: str, summary: str) -> str:
        """确定论文分类"""
        text = (title + " " + summary).lower()
        
        ai_match = any(kw.lower() in text for kw in self.AI_KEYWORDS)
        security_match = any(kw.lower() in text for kw in self.SECURITY_KEYWORDS)
        
        if ai_match and security_match:
            return "academic_cross"
        elif security_match:
            return "academic_security"
        else:
            return "academic_ai"


class SemanticScholarSource(BaseSource):
    """Semantic Scholar 数据源"""

    # AI/安全相关的关键词
    SEARCH_QUERIES = [
        "large language model",
        "machine learning security",
        "adversarial machine learning",
        "AI safety",
        "deep learning",
        "computer vision",
        "natural language processing",
    ]

    def __init__(self, timeout: int = 30):
        super().__init__(name="semantic_scholar", timeout=timeout)
        self.base_url = "https://api.semanticscholar.org/graph/v1"

    async def fetch(self, limit: int = 20) -> list[CollectedItem]:
        """获取 Semantic Scholar 最新论文"""
        items = []
        timeout = self.config.get("timeout", 30)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                # 搜索多个关键词
                for query in self.SEARCH_QUERIES[:2]:  # 先查询前两个关键词
                    try:
                        query_items = await self._search(client, query, limit // 2)
                        items.extend(query_items)
                    except Exception as e:
                        logger.warning(f"[SemanticScholar] 搜索 '{query}' 失败: {e}")
                        continue
                    
                    await asyncio.sleep(0.5)
                    
            except httpx.TimeoutException:
                raise SourceTimeoutError("Semantic Scholar 请求超时")
            except Exception as e:
                raise SourceConnectionError(f"Semantic Scholar 连接失败: {e}")

        # 去重
        seen_urls = set()
        unique_items = []
        for item in items:
            if item.source_url not in seen_urls:
                seen_urls.add(item.source_url)
                unique_items.append(item)

        logger.info(f"[SemanticScholar] 成功获取 {len(unique_items)} 篇论文")
        return unique_items[:limit]

    async def _search(
        self, 
        client: httpx.AsyncClient, 
        query: str, 
        limit: int
    ) -> list[CollectedItem]:
        """搜索论文"""
        items = []
        
        url = f"{self.base_url}/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,abstract,url,authors,year,publicationDate,venue,openAccessPdf",
            "year": f"{datetime.now().year - 1}-",  # 最近两年的论文
        }
        
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        for paper in data.get("data", []):
            try:
                item = self._parse_paper(paper)
                if item:
                    items.append(item)
            except Exception as e:
                logger.debug(f"[SemanticScholar] 解析论文失败: {e}")
                continue
                
        return items

    def _parse_paper(self, paper: dict) -> Optional[CollectedItem]:
        """解析论文数据"""
        title = paper.get("title", "")
        if not title:
            return None
            
        abstract = paper.get("abstract", "")
        summary = abstract or title
        
        # 构建链接
        source_url = paper.get("url", "")
        if not source_url:
            paper_id = paper.get("paperId", "")
            source_url = f"https://www.semanticscholar.org/paper/{paper_id}"
        
        # 发布日期
        published_date = None
        pub_date = paper.get("publicationDate")
        if pub_date:
            try:
                published_date = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            except:
                pass
        
        # 确定分类
        category = self._determine_category(title, summary)
        
        # 作者
        authors = []
        for author in paper.get("authors", []):
            if author.get("name"):
                authors.append(author["name"])
        
        return CollectedItem(
            title=title,
            source="semantic_scholar",
            source_url=source_url,
            category=category,
            raw_content=abstract,
            summary=summary,
            authors=authors if authors else None,
            published_date=published_date,
            tags=["semantic_scholar", paper.get("venue", "")],
            metadata={
                "paper_id": paper.get("paperId"),
                "venue": paper.get("venue"),
                "year": paper.get("year"),
                "open_access_pdf": paper.get("openAccessPdf", {}).get("url") if paper.get("openAccessPdf") else None,
            },
        )

    def _determine_category(self, title: str, summary: str) -> str:
        """确定论文分类"""
        text = (title + " " + (summary or "")).lower()
        
        security_keywords = ["security", "privacy", "adversarial", "attack", "vulnerability", "safety"]
        has_security = any(kw in text for kw in security_keywords)
        has_ai = True  # 因为搜索的是 AI 相关关键词
        
        if has_security and has_ai:
            return "academic_cross"
        elif has_security:
            return "academic_security"
        else:
            return "academic_ai"


class PapersWithCodeSource(BaseSource):
    """Papers with Code 数据源"""

    def __init__(self, timeout: int = 30):
        super().__init__(name="papers_with_code", timeout=timeout)
        self.base_url = "https://paperswithcode.com/api/v1"

    async def fetch(self, limit: int = 20) -> list[CollectedItem]:
        """获取 Papers with Code 最新论文"""
        items = []
        timeout = self.config.get("timeout", 30)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                # 获取最新论文
                url = f"{self.base_url}/papers/"
                params = {
                    "ordering": "-published",
                    "page": 1,
                    "items_per_page": limit,
                }
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                for paper in data.get("results", []):
                    try:
                        item = self._parse_paper(paper)
                        if item:
                            items.append(item)
                    except Exception as e:
                        logger.debug(f"[PapersWithCode] 解析论文失败: {e}")
                        continue
                        
            except httpx.TimeoutException:
                raise SourceTimeoutError("Papers with Code 请求超时")
            except Exception as e:
                raise SourceConnectionError(f"Papers with Code 连接失败: {e}")

        logger.info(f"[PapersWithCode] 成功获取 {len(items)} 篇论文")
        return items

    def _parse_paper(self, paper: dict) -> Optional[CollectedItem]:
        """解析论文数据"""
        title = paper.get("title", "")
        if not title:
            return None
            
        abstract = paper.get("abstract", "")
        summary = abstract or title
        
        # 链接
        source_url = paper.get("url_abs", paper.get("url_pdf", ""))
        if not source_url:
            source_url = f"https://paperswithcode.com/paper/{paper.get('id', '')}"
        
        # 发布日期
        published_date = None
        pub_date = paper.get("published")
        if pub_date:
            try:
                published_date = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            except:
                pass
        
        # 确定分类（基于领域）
        area = paper.get("area", "").lower()
        if "security" in area or "privacy" in area:
            category = "academic_security"
        else:
            category = "academic_ai"
        
        return CollectedItem(
            title=title,
            source="papers_with_code",
            source_url=source_url,
            category=category,
            raw_content=abstract,
            summary=summary,
            authors=paper.get("authors", []),
            published_date=published_date,
            tags=["papers_with_code", area],
            metadata={
                "paper_id": paper.get("id"),
                "area": area,
                "stars": paper.get("stars", 0),
                "github_url": paper.get("github", ""),
            },
        )
