"""内容总结器"""
import json
from dataclasses import dataclass
from typing import Optional

from langchain_core.language_models import BaseChatModel

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import SummarizationError
from src.agents.analyzer.prompts import get_summary_prompt

logger = get_logger(__name__)


@dataclass
class SummaryResult:
    """总结结果"""
    summary: str
    key_points: list[str]
    learning_suggestions: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "key_points": self.key_points,
            "learning_suggestions": self.learning_suggestions,
        }


class Summarizer:
    """内容总结器"""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.max_key_points = settings.max_key_points

    async def summarize(
        self,
        title: str,
        source: str,
        category: str,
        content: str,
    ) -> SummaryResult:
        """
        生成内容总结

        Args:
            title: 标题
            source: 来源
            category: 分类
            content: 内容

        Returns:
            SummaryResult 总结结果
        """
        try:
            # 截断过长的内容
            max_content_length = 3000
            truncated_content = content[:max_content_length]
            if len(content) > max_content_length:
                truncated_content += "...(内容已截断)"

            # 使用智能选择的 prompt（自动检测语言）
            prompt = get_summary_prompt(
                title=title,
                source=source,
                category=category,
                content=truncated_content,
                max_key_points=self.max_key_points,
            )

            response = await self.llm.ainvoke(prompt)
            result = self._parse_response(response.content if hasattr(response, "content") else str(response))

            return SummaryResult(
                summary=result.get("summary", "无法生成总结"),
                key_points=result.get("key_points", []),
                learning_suggestions=result.get("learning_suggestions"),
            )

        except Exception as e:
            logger.error(f"总结生成失败: {e}")
            raise SummarizationError(f"总结生成失败: {e}")

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
            "summary": response[:200] if len(response) > 200 else response,
            "key_points": [],
            "learning_suggestions": None,
        }
