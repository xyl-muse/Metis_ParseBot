"""核心配置模块 - 使用环境变量管理配置"""
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类 - 从环境变量加载"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==================== 应用配置 ====================
    app_name: str = "Metis_ParseBot"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    # ==================== LLM API 配置 ====================
    openai_api_key: Optional[str] = None
    openai_api_base: str = "https://api.openai.com/v1"
    model_name: str = "gpt-4"
    model_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4000, ge=1)

    # 备用 API 配置
    anthropic_api_key: Optional[str] = None

    @field_validator("openai_api_key", "anthropic_api_key")
    @classmethod
    def validate_api_key(cls, v: Optional[str]) -> Optional[str]:
        """验证 API Key 格式"""
        if v is not None and not v.startswith(("sk-", "sk-ant-")):
            # 允许其他格式的 API Key，只做警告
            pass
        return v

    # ==================== 数据库配置 ====================
    database_url: str = "sqlite+aiosqlite:///./data/metis.db"
    database_echo: bool = False

    # ==================== 采集配置 ====================
    collect_interval_hours: int = Field(default=6, ge=1, le=24)
    max_items_per_run: int = Field(default=50, ge=1, le=200)
    collect_timeout_seconds: int = Field(default=30, ge=10)
    content_age_limit_days: int = Field(default=3, ge=1, le=30)  # 内容时效性限制（天）

    # arXiv 配置
    arxiv_categories: list[str] = Field(
        default=["cs.AI", "cs.CL", "cs.LG", "cs.CR", "cs.CV"]
    )
    arxiv_max_results: int = Field(default=20, ge=1, le=100)

    # 新闻源配置
    news_sources: list[str] = Field(
        default=["hackernews", "reddit_ml", "reddit_security"]
    )

    # ==================== 预审配置 ====================
    passing_score: int = Field(default=60, ge=0, le=100)
    score_weights: dict[str, float] = Field(
        default={
            "novelty": 0.25,        # 新颖性
            "utility": 0.25,        # 实用性
            "authority": 0.20,      # 权威性
            "timeliness": 0.15,     # 时效性
            "completeness": 0.15,   # 完整性
        }
    )

    # ==================== 分析配置 ====================
    max_knowledge_links: int = Field(default=5, ge=1, le=10)
    max_key_points: int = Field(default=10, ge=1, le=20)

    # ==================== API 服务配置 ====================
    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_workers: int = Field(default=1, ge=1)
    cors_origins: list[str] = Field(default=["http://localhost:3000", "http://localhost:5173"])

    # ==================== 缓存配置 ====================
    enable_cache: bool = True
    cache_ttl_seconds: int = Field(default=3600, ge=60)

    def get_effective_api_key(self) -> str:
        """获取有效的 API Key"""
        if self.openai_api_key:
            return self.openai_api_key
        if self.anthropic_api_key:
            return self.anthropic_api_key
        raise ValueError("未配置任何有效的 LLM API Key")

    def get_llm_provider(self) -> str:
        """确定使用的 LLM 提供商"""
        if self.openai_api_key:
            return "openai"
        if self.anthropic_api_key:
            return "anthropic"
        raise ValueError("未配置任何 LLM 提供商")


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 导出配置实例
settings = get_settings()
