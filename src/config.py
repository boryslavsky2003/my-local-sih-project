"""
Конфігурація застосунку.
Використовує pydantic-settings для читання .env / змінних оточення.
"""

from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMBackend(str, Enum):
    """Підтримувані бекенди LLM."""
    OLLAMA = "ollama"
    OPENAI_COMPATIBLE = "openai_compatible"


class Settings(BaseSettings):
    """Головний клас налаштувань."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Telegram ──────────────────────────────────────────────
    BOT_TOKEN: str = ""

    # ── LLM Backend ───────────────────────────────────────────
    LLM_BACKEND: LLMBackend = LLMBackend.OLLAMA

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:latest"

    # OpenAI-compatible (llama.cpp, vLLM, TGI, …)
    OPENAI_API_BASE: str = "http://localhost:8080/v1"
    OPENAI_API_KEY: str = "not-needed"
    OPENAI_MODEL: str = "local-model"

    # ── Chat ──────────────────────────────────────────────────
    SYSTEM_PROMPT: str = "Ти — корисний асистент. Відповідай українською мовою."
    MAX_HISTORY_LENGTH: int = 20  # пар повідомлень
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.7

    # ── Available models (для вибору) ────────────────────────
    AVAILABLE_MODELS: list[str] = [
        "llama3.2:latest",
        "deepseek-coder-v2:16b",
        "richardyoung/gemma-4-12b-coder-abliterated:latest",
    ]


settings = Settings()  # єдиний екземпляр
