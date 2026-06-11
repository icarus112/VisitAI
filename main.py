import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
import logging

from aiogram.exceptions import TelegramNetworkError

from app.ai.ai_intent import AIIntentService
from app.service.embedding import EmbeddingService
from logs import logger
from database.async_engine import async_session
from app.core.middlewares import AppMiddleware
from app.core.routers import router
from conf import BOT_TOKEN, BOT_PROXY, AI_API

# @router.message(CommandStart)
# async def health_check(message: Message):
#     await message.answer("I'm alive")

logger = logging.getLogger(__name__)

"""
из-за проблем с инет лучше проверить доступен ли тг апи, это делает wait_tg
он будет ждать после вкл пока доступ не откроется
"""
async def wait_tg(bot: Bot, delay: int = 5):
    attempt = 1

    while True:
        try:
            me = await bot.get_me(request_timeout=60)

            logger.info(
                "Telegram API is available. Bot username=%s, id=%s",
                me.username,
                me.id,
            )

            return
        except TelegramNetworkError:
            logger.warning(
                "Telegram API unavailable. Attempt %s. Retry in %s sec",
                attempt,
                delay,
            )

            attempt += 1
            await asyncio.sleep(delay)

"""
еще появилась проблема в том что бы если бот был выкл некоторое время, то у него накопятся
сообщения которые нужно обработать из-за этого лучше перед запуском удалить очередь не обработку
"""
async def safe_delete_webhook(bot: Bot, retries: int = 5, delay: int = 5):
    for attempt in range(retries):
        try:
            await bot.delete_webhook(
                drop_pending_updates=True,
                request_timeout=60,
            )

            logger.info("Webhook deleted successfully")
            return

        except TelegramNetworkError:
            logger.warning(
                "Can't delete webhook. Attempt %s/%s. Retry in %s sec",
                attempt,
                retries,
                delay,
                exc_info=True,
            )

            if attempt == retries:
                logger.error(
                    "Failed to delete webhook, but polling will be started anyway"
                )
                return

            await asyncio.sleep(delay)


async def main():
    if BOT_PROXY:
        session = AiohttpSession(proxy=BOT_PROXY)
        bot = Bot(token=BOT_TOKEN, session=session)
        logger.info(f"Proxy enabled: {BOT_PROXY}")
    else:
        bot = Bot(token=BOT_TOKEN)
        logger.info("Proxy disabled")

    dp=Dispatcher()
    em_sv = EmbeddingService( "intfloat/multilingual-e5-small",
    local_files_only=True,)
    ai_sv = AIIntentService(AI_API)
    # logging.basicConfig(level=logging.DEBUG)

    # middleware
    dp.message.outer_middleware(AppMiddleware(
        async_session, em_sv, ai_sv))
    dp.callback_query.outer_middleware(AppMiddleware(
        async_session, em_sv, ai_sv))

    #собраны все роутеры
    dp.include_router(router)

    try:
        # await bot.delete_webhook(drop_pending_updates=True)
        await wait_tg(bot)

        await safe_delete_webhook(
            bot, retries=10, delay=5
        )
        logger.info(
            "Bot started"
        )
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


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


