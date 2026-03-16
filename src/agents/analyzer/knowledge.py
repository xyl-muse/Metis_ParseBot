"""知识关联分析器"""
import json
from dataclasses import dataclass
from typing import Optional

from langchain_core.language_models import BaseChatModel

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import KnowledgeLinkError
from src.agents.analyzer.prompts import KNOWLEDGE_LINK_PROMPT

logger = get_logger(__name__)


@dataclass
class KnowledgeLink:
    """知识关联"""
    concept: str
    relation: str  # 先修/扩展/对比
    note: str

    def to_dict(self) -> dict:
        return {
            "concept": self.concept,
            "relation": self.relation,
            "note": self.note,
        }


@dataclass
class ConfusionNote:
    """易混淆辨析"""
    item: str
    distinction: str

    def to_dict(self) -> dict:
        return {
            "item": self.item,
            "distinction": self.distinction,
        }


@dataclass
class KnowledgeAnalysisResult:
    """知识关联分析结果"""
    knowledge_links: list[KnowledgeLink]
    confusion_notes: list[ConfusionNote]
    related_topics: list[str]

    def to_dict(self) -> dict:
        return {
            "knowledge_links": [k.to_dict() for k in self.knowledge_links],
            "confusion_notes": [c.to_dict() for c in self.confusion_notes],
            "related_topics": self.related_topics,
        }


class KnowledgeAnalyzer:
    """知识关联分析器"""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.max_knowledge_links = settings.max_knowledge_links

    async def analyze(
        self,
        title: str,
        summary: str,
        key_points: list[str],
    ) -> KnowledgeAnalysisResult:
        """
        分析知识关联

        Args:
            title: 标题
            summary: 总结
            key_points: 关键要点

        Returns:
            KnowledgeAnalysisResult 知识关联分析结果
        """
        try:
            prompt = KNOWLEDGE_LINK_PROMPT.format(
                title=title,
                summary=summary,
                key_points=json.dumps(key_points, ensure_ascii=False),
            )

            response = await self.llm.ainvoke(prompt)
            result = self._parse_response(response.content if hasattr(response, "content") else str(response))

            # 构建知识关联列表
            knowledge_links = []
            for link_data in result.get("knowledge_links", [])[:self.max_knowledge_links]:
                knowledge_links.append(KnowledgeLink(
                    concept=link_data.get("concept", ""),
                    relation=link_data.get("relation", ""),
                    note=link_data.get("note", ""),
                ))

            # 构建易混淆辨析列表
            confusion_notes = []
            for confusion_data in result.get("confusion_notes", []):
                confusion_notes.append(ConfusionNote(
                    item=confusion_data.get("item", ""),
                    distinction=confusion_data.get("distinction", ""),
                ))

            return KnowledgeAnalysisResult(
                knowledge_links=knowledge_links,
                confusion_notes=confusion_notes,
                related_topics=result.get("related_topics", []),
            )

        except Exception as e:
            logger.error(f"知识关联分析失败: {e}")
            raise KnowledgeLinkError(f"知识关联分析失败: {e}")

    def _parse_response(self, response: str) -> dict:
        """解析 LLM 响应"""
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        return {
            "knowledge_links": [],
            "confusion_notes": [],
            "related_topics": [],
        }
