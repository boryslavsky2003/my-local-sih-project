"""
LLM Service — оркеструє генерацію, обирає бекенд,
потоково повертає результат.
"""

from typing import AsyncIterator

from src.config import LLMBackend, settings
from src.llm.base import LLMClient
from src.llm.ollama_client import OllamaClient


class LLMService:
    """
    Сервіс для роботи з LLM.
    Автоматично створює потрібний клієнт залежно від LLM_BACKEND.
    """

    def __init__(self) -> None:
        self._client: LLMClient = self._build_client()

    # ------------------------------------------------------------------
    @staticmethod
    def _build_client() -> LLMClient:
        if settings.LLM_BACKEND == LLMBackend.OLLAMA:
            return OllamaClient()
        # Тут можна додати OpenAICompatibleClient(...)
        raise ValueError(f"Невідомий LLM_BACKEND: {settings.LLM_BACKEND}")

    # ------------------------------------------------------------------
    async def generate(
        self,
        messages: list[dict],
    ) -> str:
        """Повна (не потокова) генерація."""
        return await self._client.generate(
            messages=messages,
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE,
        )

    # ------------------------------------------------------------------
    async def generate_stream(
        self,
        messages: list[dict],
    ) -> AsyncIterator[str]:
        """Потокова генерація — видає токени в міру надходження."""
        async for token in self._client.generate_stream(
            messages=messages,
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE,
        ):
            yield token

    # ------------------------------------------------------------------
    def _get_client_for_model(self, model: str) -> LLMClient:
        """Повертає клієнт для конкретної моделі (або дефолтний)."""
        if settings.LLM_BACKEND == LLMBackend.OLLAMA:
            return OllamaClient(model=model)
        raise ValueError(f"Невідомий LLM_BACKEND: {settings.LLM_BACKEND}")

    async def generate_with_progress(
        self,
        messages: list[dict],
        progress_callback: callable,
        batch_size: int = 5,
        model: str = "",
    ) -> str:
        """
        Генерація з проміжним колбеком для оновлення повідомлення в Telegram.
        `progress_callback(text)` викликається кожні `batch_size` токенів.
        `model` — модель для цього запиту (якщо порожньо — береться з налаштувань).
        Повертає повний зібраний текст.
        """
        client = self._get_client_for_model(model) if model else self._client

        full_text = ""
        buffer = ""

        async for token in client.generate_stream(
            messages=messages,
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE,
        ):
            full_text += token
            buffer += token

            if len(buffer) >= batch_size:
                await progress_callback(full_text)
                buffer = ""

        # фінальне оновлення
        if buffer:
            await progress_callback(full_text)

        return full_text
