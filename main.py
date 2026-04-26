import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.client.session.aiohttp import AiohttpSession

from app.core.middlewares import AppMiddleware
from app.core.routers import router
from conf import BOT_TOKEN, BOT_PROXY
import logging

# @router.message(CommandStart)
# async def health_check(message: Message):
#     await message.answer("I'm alive")

async def main():
    if BOT_PROXY:
        session = AiohttpSession(proxy=BOT_PROXY)
        bot = Bot(token=BOT_TOKEN, session=session)
        print(f"Proxy enabled: {BOT_PROXY}")
    else:
        bot = Bot(token=BOT_TOKEN)
        print("Proxy disabled")
    dp=Dispatcher()
    logging.basicConfig(level=logging.DEBUG)

    # middleware
    dp.message.middleware(AppMiddleware())
    dp.callback_query.middleware(AppMiddleware())

    #собраны все роутеры
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("бот выкл.")