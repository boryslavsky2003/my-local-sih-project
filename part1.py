"""
Хендлери команд та текстових повідомлень.
"""

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import (
    confirm_clear_keyboard,
    main_keyboard,
    message_actions_keyboard,
    model_selection_keyboard,
)
from src.config import settings as app_settings
from src.llm.service import LLMService
from src.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = Router()

_chat_service: ChatService = None  # type: ignore[assignment]
_llm_service: LLMService = None   # type: ignore[assignment]


def setup(chat_service: ChatService, llm_service: LLMService) -> None:
    global _chat_service, _llm_service
    _chat_service = chat_service
    _llm_service = llm_service


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 <b>Вітаю!</b>\n\n"
        "Я — бот, що спілкується з локальною LLM.\n"
        "Просто напиши мені повідомлення — і я відповім.\n\n"
        "Доступні команди:\n"
        "/start — це повідомлення\n"
        "/new — почати новий діалог\n"
        "/model — вибрати модель\n"
        "/clear — очистити історію\n"
        "/history — показати історію діалогу\n"
        "/help — довідка",
        reply_markup=main_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "🤖 <b>Як це працює:</b>\n\n"
        "1. Ти надсилаєш повідомлення\n"
        "2. Бот передає його локальній LLM (Ollama)\n"
        "3. Відповідь з'являється в чаті (з потоковим друком)\n\n"
        "Модель працює на твоєму ноутбуці — ніяких зовнішніх API!\n\n"
        "Команди:\n"
        "/new — новий діалог\n"
        "/model — вибрати модель\n"
        "/clear — очистити історію\n"
        "/history — показати історію",
    )


@router.message(Command("model"))
@router.message(F.text == "🧠 Модель")
async def cmd_model(message: Message) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    session = _chat_service.get_or_create(user_id)
    await message.answer(
        f"🧠 <b>Поточна модель:</b>\n<code>{session.model}</code>\n\n"
        "Оберіть модель зі списку нижче:",
        reply_markup=model_selection_keyboard(
            available_models=app_settings.AVAILABLE_MODELS,
            current_model=session.model,
        ),
    )


@router.message(Command("new"))
@router.message(F.text == "🆕 Новий діалог")
async def cmd_new_chat(message: Message) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    _chat_service.clear_session(user_id)
    await message.answer(
        "🆕 <b>Новий діалог розпочато!</b>\n\n"
        "Історію очищено. Тепер я не пам'ятаю попередніх повідомлень.",
        reply_markup=main_keyboard(),
    )


@router.message(Command("clear"))
async def cmd_clear(message: Message) -> None:
    await message.answer(
        "❓ <b>Ви впевнені, що хочете очистити історію діалогу?</b>",
        reply_markup=confirm_clear_keyboard(),
    )


@router.message(Command("history"))
@router.message(F.text == "📜 Історія")
async def cmd_history(message: Message) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    session = _chat_service.get_session(user_id)
    if not session or not session.messages:
        await message.answer("📜 Історія порожня. Почни діалог!")
        return
    lines = ["<b>📜 Історія діалогу:</b>\n"]
    for msg in session.messages[-10:]:
        role = "👤 Ти" if msg["role"] == "user" else "🤖 Бот"
        content = msg["content"][:100] + "…" if len(msg["content"]) > 100 else msg["content"]
        lines.append(f"{role}: {content}\n")
    await message.answer("\n".join(lines))


@router.message(F.text == "ℹ️ Про бота")
async def cmd_about(message: Message) -> None:
    await message.answer(
        "🤖 <b>Local LLM Telegram Bot</b>\n\n"
        "Працює виключно з локальною моделлю через Ollama.\n"
        "Жодні дані не передаються в інтернет.\n\n"
        "Стек: aiogram 3.x + Ollama\n"
        "Мова: Python 3.11+",
    )
