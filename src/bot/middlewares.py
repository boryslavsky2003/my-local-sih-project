"""
Middlewares для aiogram 3.x.
"""

import logging
import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    """
    Обмеження частоти повідомлень від одного користувача.
    """

    def __init__(self, rate_limit: float = 1.0) -> None:
        self.rate_limit = rate_limit
        self._last_time: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
            now = time.monotonic()
            last = self._last_time.get(user_id, 0.0)

            if now - last < self.rate_limit:
                logger.warning("Throttling user_id=%s", user_id)
                return  # ігноруємо повідомлення

            self._last_time[user_id] = now

        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    """Логування вхідних повідомлень."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            logger.info(
                "[%s] %s: %s",
                event.from_user.id if event.from_user else "?",
                event.from_user.full_name if event.from_user else "?",
                event.text or "[non-text]",
            )
        return await handler(event, data)
