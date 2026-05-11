from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from app.core import keyboards as kb
from app.core.states import AiUserState

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message,
                        state: FSMContext):

    await message.answer(
        "Привет 👋\n\n"
        "Я AI-помощник для записи на услуги.")

    await message.answer(
        "Можете написать обычным текстом:\n"
        "• Хочу записаться на массаж завтра в 14:00\n"
        "• Какие услуги есть для боли в спине?\n"
        "• Покажи мои записи"
    )

    await message.answer(
        "Или открыть обычное меню 👇",
        reply_markup=kb.main
    )

    await state.set_state(AiUserState.chatting)