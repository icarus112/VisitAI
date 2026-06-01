import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.client.session.aiohttp import AiohttpSession
import logging

from app.core import logger
from database.async_engine import async_session
from app.core.middlewares import AppMiddleware
from app.core.routers import router
from conf import BOT_TOKEN, BOT_PROXY

# @router.message(CommandStart)
# async def health_check(message: Message):
#     await message.answer("I'm alive")

logger = logging.getLogger(__name__)

async def main():
    if BOT_PROXY:
        session = AiohttpSession(proxy=BOT_PROXY)
        bot = Bot(token=BOT_TOKEN, session=session)
        logger.info(f"Proxy enabled: {BOT_PROXY}")
    else:
        bot = Bot(token=BOT_TOKEN)
        logger.info("Proxy disabled")
    dp=Dispatcher()
    # logging.basicConfig(level=logging.DEBUG)

    # middleware
    dp.message.outer_middleware(AppMiddleware(async_session))
    dp.callback_query.outer_middleware(AppMiddleware(async_session))

    #собраны все роутеры
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

    logger.info(
        "Bot started"
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info(
            "Bot stopped by KeyboardInterrupt"
        )

    except Exception:
        logger.exception(
            "Fatal error while running bot"
        )