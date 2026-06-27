"""
Точка входу в бота.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Додаємо корінь проєкту в sys.path,
# щоб можна було запускати як `python src/main.py`, так і `python -m src.main`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.bot.handlers import router as handlers_router
from src.bot.handlers import setup as setup_handlers
from src.bot.middlewares import LoggingMiddleware, ThrottlingMiddleware
from src.config import settings
from src.llm.service import LLMService
from src.services.chat_service import ChatService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Головна функція запуску бота."""

    # ── Перевірка токена ───────────────────────────────────────
    if not settings.BOT_TOKEN:
        logger.error("BOT_TOKEN не задано! Скопіюй .env.example → .env та заповни токен.")
        return

    # ── Ініціалізація сервісів ──────────────────────────────────
    _chat_service = ChatService()
    _llm_service = LLMService()

    # Інжекція залежностей у хендлери
    setup_handlers(chat_service=_chat_service, llm_service=_llm_service)

    # ── Створюємо бота та диспетчер ────────────────────────────
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # ── Middlewares ─────────────────────────────────────────────
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(ThrottlingMiddleware(rate_limit=1.0))

    # ── Реєструємо роутер з хендлерами ─────────────────────────
    dp.include_router(handlers_router)

    # ── Пропустити накопичені апдейти та старт ─────────────────
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info(
        "Бот запущено! Backend: %s, Model: %s",
        settings.LLM_BACKEND.value,
        settings.OLLAMA_MODEL,
    )

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

