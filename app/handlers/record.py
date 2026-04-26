from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.core import keyboards as kb
from app.core.States import RecordState
from app.service.user import UserService

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):

    await message.answer(
        "Привет 👋\nЯ помогу записаться на услугу."
        "\n\nНапиши, что тебе нужно 🙂",
        reply_markup=kb.main)

@router.message(F.text == "✏️Добавить запись")
async def add_record(message: Message, state: FSMContext, us_sv: UserService):

    user = await us_sv.get_by_tg_id(message.from_user.id)
    if not user:
        await message.answer(f"давайте авторизуемся, мы можешь вас называть {message.from_user.username}?")

# @router.message(RecordState.check_authorization)
# async def check_auth(message: Message, state: FSMContext):
#     # auth = False#await rd_sv.check_authorization(message.from_user.id)
#     # if not auth:
#     await message.answer(f"давайте авторизуемся, мы можешь вас называть {message.from_user.username}?")