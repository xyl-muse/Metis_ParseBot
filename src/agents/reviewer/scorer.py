"""评分引擎"""
import json
from dataclasses import dataclass
from typing import Optional

from langchain_core.language_models import BaseChatModel

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import ScoringError
from src.agents.reviewer.prompts import SCORING_PROMPT, REJECTION_REASON_PROMPT

logger = get_logger(__name__)


@dataclass
class ScoreResult:
    """评分结果"""
    novelty_score: int
    utility_score: int
    authority_score: int
    timeliness_score: int
    completeness_score: int
    total_score: float
    passed: bool
    brief_reason: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "novelty_score": self.novelty_score,
            "utility_score": self.utility_score,
            "authority_score": self.authority_score,
            "timeliness_score": self.timeliness_score,
            "completeness_score": self.completeness_score,
            "total_score": self.total_score,
            "passed": self.passed,
            "brief_reason": self.brief_reason,
        }


class Scorer:
    """内容评分引擎"""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.weights = settings.score_weights
        self.passing_score = settings.passing_score

    async def score(
        self,
        title: str,
        source: str,
        category: str,
        summary: str,
    ) -> ScoreResult:
        """
        对内容进行评分

        Args:
            title: 标题
            source: 来源
            category: 分类
            summary: 摘要

        Returns:
            ScoreResult 评分结果
        """
        try:
            prompt = SCORING_PROMPT.format(
                title=title,
                source=source,
                category=category,
                summary=summary or title,
            )

            response = await self.llm.ainvoke(prompt)
            
            # 解析响应
            content = response.content if hasattr(response, "content") else str(response)
            result = self._parse_response(content)

            # 计算加权总分
            total_score = self._calculate_weighted_score(result)

            # 判断是否通过
            passed = total_score >= self.passing_score

            return ScoreResult(
                novelty_score=result.get("novelty_score", 50),
                utility_score=result.get("utility_score", 50),
                authority_score=result.get("authority_score", 50),
                timeliness_score=result.get("timeliness_score", 50),
                completeness_score=result.get("completeness_score", 50),
                total_score=total_score,
                passed=passed,
                brief_reason=result.get("brief_reason"),
            )

        except Exception as e:
            logger.error(f"评分失败: {e}")
            raise ScoringError(f"评分失败: {e}")

    def _parse_response(self, response: str) -> dict:
        """解析 LLM 响应"""
        try:
            # 提取 JSON 部分
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # 返回默认值
        return {
            "novelty_score": 50,
            "utility_score": 50,
            "authority_score": 50,
            "timeliness_score": 50,
            "completeness_score": 50,
            "brief_reason": "无法解析评分结果",
        }

    def _calculate_weighted_score(self, scores: dict) -> float:
        """计算加权总分"""
        total = 0.0
        for key, weight in self.weights.items():
            score_key = f"{key}_score"
            if score_key in scores:
                total += scores[score_key] * weight
        return round(total, 2)

    async def get_rejection_reason(
        self,
        title: str,
        scores: ScoreResult,
    ) -> str:
        """获取拒绝原因"""
        try:
            prompt = REJECTION_REASON_PROMPT.format(
                title=title,
                novelty=scores.novelty_score,
                utility=scores.utility_score,
                authority=scores.authority_score,
                timeliness=scores.timeliness_score,
                completeness=scores.completeness_score,
                total_score=scores.total_score,
                passing_score=self.passing_score,
            )

            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, "content") else str(response)

        except Exception as e:
            logger.warning(f"获取拒绝原因失败: {e}")
            return "综合评分未达及格线"
