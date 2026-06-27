"""
Реалізація LLMClient через Ollama API.
Документація: https://github.com/ollama/ollama/blob/main/docs/api.md
"""

import json
from typing import AsyncIterator

import aiohttp

from src.config import settings
from src.llm.base import LLMClient


class OllamaClient(LLMClient):
    """Клієнт для Ollama (локальний REST API)."""

    def __init__(self, base_url: str = "", model: str = "") -> None:
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

    # ------------------------------------------------------------------
    async def generate(
        self,
        messages: list[dict],
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        """Повний запит — відповідь одним блоком."""
        payload = {
            "model": self.model,
            "messages": messages,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
            "stream": False,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data.get("message", {}).get("content", "")

    # ------------------------------------------------------------------
    async def generate_stream(
        self,
        messages: list[dict],
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Потокова генерація — кожен токен окремо (SSE-подібний формат)."""
        payload = {
            "model": self.model,
            "messages": messages,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
            "stream": True,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as resp:
                resp.raise_for_status()

                # Ollama повертає NDJSON — по одному JSON-рядку на токен
                async for line in resp.content:
                    if not line:
                        break
                    decoded = line.decode("utf-8", errors="replace").strip()
                    if not decoded:
                        continue
                    try:
                        chunk = json.loads(decoded)
                    except json.JSONDecodeError:
                        continue

                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token

                    # done = True на останньому чанку
                    if chunk.get("done"):
                        break
