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

# Сервіси — встановлюються через setup()
_chat_service: ChatService = None  # type: ignore[assignment]
_llm_service: LLMService = None   # type: ignore[assignment]


def setup(chat_service: ChatService, llm_service: LLMService) -> None:
    """Інжекція залежностей у модуль хендлерів."""
    global _chat_service, _llm_service
    _chat_service = chat_service
    _llm_service = llm_service


# ====================================================================
# КОМАНДИ
# ====================================================================

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Стартове повідомлення."""
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
    """Довідка."""
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
    """Показати меню вибору моделі."""
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
    """Почати новий діалог (очистити історію)."""
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
    """Запит на очищення історії."""
    await message.answer(
        "❓ <b>Ви впевнені, що хочете очистити історію діалогу?</b>",
        reply_markup=confirm_clear_keyboard(),
    )


@router.message(Command("history"))
@router.message(F.text == "📜 Історія")
async def cmd_history(message: Message) -> None:
    """Показати історію діалогу."""
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
    """Інформація про бота."""
    await message.answer(
        "🤖 <b>Local LLM Telegram Bot</b>\n\n"
        "Працює виключно з локальною моделлю через Ollama.\n"
        "Жодні дані не передаються в інтернет.\n\n"
        "Стек: aiogram 3.x + Ollama\n"
        "Мова: Python 3.11+",
    )


# ====================================================================
# CALLBACK-QUERIES
# ====================================================================

@router.callback_query(F.data == "new_chat")
async def callback_new_chat(callback: CallbackQuery) -> None:
    """Inline-кнопка «Новий діалог»."""
    if not callback.from_user:
        return
    user_id = callback.from_user.id
    _chat_service.clear_session(user_id)
    await callback.message.edit_text("🆕 Новий діалог розпочато!")
    await callback.answer()


@router.callback_query(F.data == "clear_history")
async def callback_clear_history(callback: CallbackQuery) -> None:
    """Inline-кнопка «Очистити історію»."""
    if not callback.message:
        return
    await callback.message.edit_text(
        "❓ <b>Ви впевнені?</b>",
        reply_markup=confirm_clear_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_clear")
async def callback_confirm_clear(callback: CallbackQuery) -> None:
    """Підтвердження очищення історії."""
    if not callback.from_user:
        return
    user_id = callback.from_user.id
    _chat_service.clear_session(user_id)
    await callback.message.edit_text("🗑 Історію очищено!")
    await callback.answer()


@router.callback_query(F.data == "cancel_clear")
async def callback_cancel_clear(callback: CallbackQuery) -> None:
    """Скасування очищення."""
    if not callback.message:
        return
    await callback.message.edit_text("❌ Очищення скасовано.")
    await callback.answer()


@router.callback_query(F.data.startswith("select_model:"))
async def callback_select_model(callback: CallbackQuery) -> None:
    """Вибір моделі з inline-клавіатури."""
    if not callback.data or not callback.from_user:
        return
    model = callback.data.removeprefix("select_model:")
    user_id = callback.from_user.id
    session = _chat_service.get_or_create(user_id)
    session.set_model(model)

    await callback.message.edit_text(
        f"✅ <b>Модель змінено!</b>\n\n"
        f"Активна модель: <code>{model}</code>\n\n"
        f"💡 Історія діалогу збережена, але нова модель не знає "
        f"про попередні повідомлення.",
    )
    await callback.answer()


# ====================================================================
# ТЕКСТОВІ ПОВІДОМЛЕННЯ (основний діалог з LLM)
# ====================================================================

@router.message(F.text)
async def handle_message(message: Message) -> None:
    """
    Головний хендлер — отримує текст, передає LLM, повертає відповідь.
    Використовує потокову генерацію з оновленням повідомлення.
    """
    if not message.from_user or not message.text:
        return

    user_id = message.from_user.id
    user_text = message.text.strip()

    if not user_text:
        return

    # 1. Зберігаємо повідомлення користувача
    session = _chat_service.get_or_create(user_id)
    session.add_message("user", user_text)
    context = session.get_context()

    # 2. Надсилаємо "друкує..."
    sent_msg = await message.answer("🤔 *Думаю…*", parse_mode="Markdown")

    # 3. Потокова генерація
    async def update_message(text: str) -> None:
        """Оновлює текст повідомлення в Telegram."""
        try:
            display = f"🤖 *Відповідь:*\n\n{text}"
            if len(display) > 4000:
                display = display[:4000] + "…"
            await sent_msg.edit_text(display, parse_mode="Markdown")
        except Exception as exc:
            logger.debug("Update error: %s", exc)

    try:
        full_response = await _llm_service.generate_with_progress(
            messages=context,
            progress_callback=update_message,
            batch_size=5,
            model=session.model,
        )
    except Exception:
        logger.exception("LLM generation failed")
        await sent_msg.edit_text(
            "❌ *Помилка генерації.*\n"
            "Переконайся, що Ollama запущена:\n"
            "```bash\nollama serve\n```",
            parse_mode="Markdown",
        )
        return

    # 4. Зберігаємо відповідь асистента
    session.add_message("assistant", full_response)

    # 5. Фінальне оновлення з клавіатурою дій
    try:
        display = f"🤖 *Відповідь:*\n\n{full_response}"
        if len(display) > 4000:
            display = display[:4000] + "…"
        await sent_msg.edit_text(
            display,
            parse_mode="Markdown",
            reply_markup=message_actions_keyboard(),
        )
    except Exception as exc:
        logger.debug("Final update error: %s", exc)
