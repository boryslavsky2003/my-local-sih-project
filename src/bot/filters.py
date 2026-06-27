"""
Кастомні фільтри для aiogram 3.x.
"""

from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class ChatTypeFilter(BaseFilter):
    """Фільтр за типом чату (private / group / supergroup)."""

    def __init__(self, chat_type: Union[str, list[str]]) -> None:
        self.chat_type = [chat_type] if isinstance(chat_type, str) else chat_type

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        if isinstance(event, CallbackQuery):
            if not event.message:
                return False
            return event.message.chat.type in self.chat_type
        return event.chat.type in self.chat_type


class IsLongMessage(BaseFilter):
    """Фільтр для довгих повідомлень (> N символів)."""

    def __init__(self, min_length: int = 100) -> None:
        self.min_length = min_length

    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        return len(message.text) > self.min_length
