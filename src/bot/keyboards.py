"""
Клавіатури для Telegram-бота.
"""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ── Головна Reply-клавіатура ─────────────────────────────────────────
def main_keyboard() -> ReplyKeyboardMarkup:
    """Основна клавіатура з швидкими діями."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆕 Новий діалог"), KeyboardButton(text="📜 Історія")],
            [KeyboardButton(text="🧠 Модель"), KeyboardButton(text="ℹ️ Про бота")],
        ],
        resize_keyboard=True,
    )


# ── Inline-клавіатура для повідомлень LLM ────────────────────────────
def message_actions_keyboard() -> InlineKeyboardMarkup:
    """Кнопки під відповіддю LLM."""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🆕 Новий діалог", callback_data="new_chat"),
        InlineKeyboardButton(text="🗑 Видалити історію", callback_data="clear_history"),
    )
    builder.adjust(2)
    return builder.as_markup()


# ── Підтвердження очищення ───────────────────────────────────────────
def confirm_clear_keyboard() -> InlineKeyboardMarkup:
    """Клавіатура підтвердження очищення історії."""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✅ Так, очистити", callback_data="confirm_clear"),
        InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_clear"),
    )
    builder.adjust(2)
    return builder.as_markup()


# ── Вибір моделі ─────────────────────────────────────────────────────
def model_selection_keyboard(
    available_models: list[str],
    current_model: str,
) -> InlineKeyboardMarkup:
    """
    Клавіатура вибору моделі.
    Біля активної моделі стоїть ✅.
    """
    builder = InlineKeyboardBuilder()
    for model in available_models:
        prefix = "✅ " if model == current_model else ""
        builder.add(
            InlineKeyboardButton(
                text=f"{prefix}{model}",
                callback_data=f"select_model:{model}",
            )
        )
    builder.adjust(1)  # кожна модель з нового рядка
    return builder.as_markup()
