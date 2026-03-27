
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers import router as fallback_router
from app.bot.routers.buy_support import router as buy_support_router
from app.bot.routers.occasion_suggestions import router as occasion_suggestions_router
from app.bot.routers.onboarding import router as onboarding_router
from app.bot.routers.rate_outfit import router as rate_outfit_router
from app.db.database import init_db
from app.utils.config import settings
from app.utils.logger import logger


async def main() -> None:
    logger.info("Starting StyleCheckAIBot...")

    await init_db()

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    # Order matters: specific routers first, catch-all last
    dp.include_router(onboarding_router)
    dp.include_router(rate_outfit_router)
    dp.include_router(occasion_suggestions_router)
    dp.include_router(buy_support_router)
    dp.include_router(fallback_router)

    logger.info("Bot is polling...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
