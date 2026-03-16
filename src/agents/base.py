"""智能体基类定义"""
from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import LLMError, LLMConnectionError

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    智能体基类
    
    所有智能体（采集、预审、分析）都应继承此类并实现 run 方法。
    """
    
    def __init__(
        self,
        name: str,
        llm: Optional[BaseChatModel] = None,
        **kwargs,
    ):
        """
        初始化智能体

        Args:
            name: 智能体名称
            llm: LLM 实例，可选。如不提供将使用默认配置创建
            **kwargs: 额外参数
        """
        self.name = name
        self._llm = llm or self._create_default_llm()
        self._kwargs = kwargs
        logger.info(f"智能体 [{name}] 初始化完成")

    @staticmethod
    def _create_default_llm() -> BaseChatModel:
        """创建默认的 LLM 实例"""
        if not settings.openai_api_key:
            raise LLMError("未配置 OpenAI API Key，请在 .env 文件中设置 OPENAI_API_KEY")
        
        return ChatOpenAI(
            model=settings.model_name,
            temperature=settings.model_temperature,
            max_tokens=settings.max_tokens,
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base,
        )

    @property
    def llm(self) -> BaseChatModel:
        """获取 LLM 实例"""
        return self._llm

    async def invoke_llm(
        self,
        prompt: str,
        **kwargs,
    ) -> str:
        """
        调用 LLM 获取响应

        Args:
            prompt: 提示词
            **kwargs: 额外参数

        Returns:
            LLM 响应文本

        Raises:
            LLMConnectionError: LLM 连接错误
            LLMError: LLM 调用错误
        """
        try:
            logger.debug(f"[{self.name}] 调用 LLM，提示词长度: {len(prompt)}")
            response = await self._llm.ainvoke(prompt, **kwargs)
            
            if isinstance(response, BaseMessage):
                result = response.content
            else:
                result = str(response)
            
            logger.debug(f"[{self.name}] LLM 响应长度: {len(result)}")
            return result
            
        except Exception as e:
            error_msg = f"LLM 调用失败: {str(e)}"
            logger.error(f"[{self.name}] {error_msg}")
            raise LLMConnectionError(error_msg) from e

    @abstractmethod
    async def run(self, *args, **kwargs) -> Any:
        """
        执行智能体任务（抽象方法，子类必须实现）

        Returns:
            任务执行结果
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"
