import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
import database
from handlers import start_router, referrals_router, admin_router, help_router, chat_member_router, inline_buttons_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


bot = Bot(BOT_TOKEN)

dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(referrals_router)
dp.include_router(admin_router)
dp.include_router(help_router)
dp.include_router(chat_member_router)
dp.include_router(inline_buttons_router)


async def main():
    try:
        logger.info("Initializing database")
        await database.init_db()
        logger.info("Removing any existing webhook and dropping pending updates")
        try:
            await bot.delete_webhook(drop_pending_updates=True)
        except Exception:
            logger.exception("Failed to delete webhook (may be fine)")

        logger.info("Starting polling")
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("Error in main: %s", e)


if __name__ == "__main__":
    asyncio.run(main())