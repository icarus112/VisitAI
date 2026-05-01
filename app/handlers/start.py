from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.core import keyboards as kb
router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):

    await message.answer(
        "Привет 👋\nЯ помогу записаться на услугу."
        "\n\nНапиши, что тебе нужно 🙂",
        reply_markup=kb.main)