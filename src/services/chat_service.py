"""
Chat Service — управління сесіями діалогів.

Кожен користувач має окрему сесію з історією повідомлень.
Історія зберігається в пам'яті (dict). При потребі можна мігрувати на Redis / DB.
"""

from dataclasses import dataclass, field
from typing import Optional

from src.config import settings
from src.utils.helpers import truncate_history


@dataclass
class ChatSession:
    """Сесія діалогу одного користувача."""

    user_id: int
    messages: list[dict] = field(default_factory=list)
    system_prompt: str = settings.SYSTEM_PROMPT
    model: str = settings.OLLAMA_MODEL

    def add_message(self, role: str, content: str) -> None:
        """Додає повідомлення та обрізає історію."""
        self.messages.append({"role": role, "content": content})
        self.messages = truncate_history(self.messages, settings.MAX_HISTORY_LENGTH)

    def get_context(self) -> list[dict]:
        """Повертає контекст з системним промптом на початку."""
        context = [{"role": "system", "content": self.system_prompt}]
        context.extend(self.messages)
        return context

    def clear(self) -> None:
        """Очищує історію (без системного промпту)."""
        self.messages.clear()

    def set_model(self, model: str) -> None:
        """Змінює активну модель."""
        self.model = model


class ChatService:
    """Сервіс, що тримає всі сесії."""

    def __init__(self) -> None:
        self._sessions: dict[int, ChatSession] = {}

    # ------------------------------------------------------------------
    def get_or_create(self, user_id: int) -> ChatSession:
        """Отримує або створює сесію для користувача."""
        if user_id not in self._sessions:
            self._sessions[user_id] = ChatSession(user_id=user_id)
        return self._sessions[user_id]

    def get_session(self, user_id: int) -> Optional[ChatSession]:
        """Отримує сесію, якщо вона існує."""
        return self._sessions.get(user_id)

    def clear_session(self, user_id: int) -> None:
        """Очищує історію для користувача."""
        session = self._sessions.get(user_id)
        if session:
            session.clear()

    def delete_session(self, user_id: int) -> None:
        """Повністю видаляє сесію."""
        self._sessions.pop(user_id, None)

    @property
    def active_sessions(self) -> int:
        """Кількість активних сесій."""
        return len(self._sessions)
