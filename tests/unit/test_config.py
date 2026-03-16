"""配置模块单元测试"""
import pytest
from unittest.mock import patch

from src.core.config import Settings


class TestSettings:
    """Settings 配置类测试"""

    def test_default_values(self):
        """测试默认值"""
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings()
            
            assert settings.app_name == "Metis_ParseBot"
            assert settings.app_version == "0.1.0"
            assert settings.debug is False
            assert settings.log_level == "INFO"
            assert settings.model_name == "gpt-4"
            assert settings.model_temperature == 0.7
            assert settings.max_tokens == 4000
            assert settings.database_url == "sqlite+aiosqlite:///./data/metis.db"
            assert settings.collect_interval_hours == 6
            assert settings.max_items_per_run == 50
            assert settings.passing_score == 60

    def test_custom_values_from_env(self):
        """测试从环境变量读取自定义值"""
        env_vars = {
            "APP_NAME": "CustomApp",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
            "MODEL_NAME": "gpt-4-turbo",
            "MODEL_TEMPERATURE": "0.5",
            "PASSING_SCORE": "70",
        }
        
        with patch.dict("os.environ", env_vars, clear=True):
            settings = Settings()
            
            assert settings.app_name == "CustomApp"
            assert settings.debug is True
            assert settings.log_level == "DEBUG"
            assert settings.model_name == "gpt-4-turbo"
            assert settings.model_temperature == 0.5
            assert settings.passing_score == 70

    def test_score_weights_default(self):
        """测试评分权重默认值"""
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings()
            
            assert settings.score_weights["novelty"] == 0.25
            assert settings.score_weights["utility"] == 0.25
            assert settings.score_weights["authority"] == 0.20
            assert settings.score_weights["timeliness"] == 0.15
            assert settings.score_weights["completeness"] == 0.15

    def test_get_llm_provider_openai(self):
        """测试获取LLM提供商 - OpenAI"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}, clear=True):
            settings = Settings()
            assert settings.get_llm_provider() == "openai"

    def test_get_llm_provider_anthropic(self):
        """测试获取LLM提供商 - Anthropic"""
        env_vars = {
            "ANTHROPIC_API_KEY": "sk-ant-test",
        }
        with patch.dict("os.environ", env_vars, clear=True):
            settings = Settings()
            assert settings.get_llm_provider() == "anthropic"

    def test_get_llm_provider_none(self):
        """测试未配置LLM时抛出异常"""
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings()
            with pytest.raises(ValueError, match="未配置任何 LLM 提供商"):
                settings.get_llm_provider()