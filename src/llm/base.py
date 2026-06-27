"""
Абстрактний інтерфейс для будь-якого LLM-бекенду.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator


class LLMClient(ABC):
    """Базовий клас для клієнтів локальних LLM."""

    @abstractmethod
    async def generate(
        self,
        messages: list[dict],
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        """Повна генерація відповіді (один string)."""
        ...

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[dict],
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Генерація з потоковою видачею токенів."""
        ...
