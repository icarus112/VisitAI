from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.core.states import CreateUserState
from app.core import keyboards as kb
from app.handlers.record import show_catalogs
from app.service.catalog import CatalogService
from app.service.user import UserService

router = Router()

'''
========================================================================================
                                     ЕСЛИ ЮЗЕР НЕ АВТОРИЗОВАН
========================================================================================
'''
@router.callback_query(F.data == "accept_name", CreateUserState.ask_name)
async def accept_name(callback: CallbackQuery, state: FSMContext):
    # await callback.message.edit_reply_markup(reply_markup=None)  # ← убрали кнопки
    data = await state.get_data()
    name = data.get("suggested_name")

    await state.update_data(name=name)

    await callback.message.edit_text(
        "✅ Имя подтверждено",
        reply_markup=None
    )

    name_obj = callback.from_user.username or callback.from_user.first_name
    await callback.message.answer("Отлично 😄, хотите ли вы добавить свой номер что-бы " 
                         "можно бы с вами связяться?", reply_markup=kb.get_number)

    await state.set_state(CreateUserState.ask_number)
    await callback.answer()


@router.callback_query(F.data == "reject_name", CreateUserState.ask_name)
async def create_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Хорошо 🙂, прошу введите пожалуйста ваше имя:")
    await state.set_state(CreateUserState.get_name)
    await callback.answer()

@router.message(CreateUserState.get_name)
async def get_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Введите имя текстом")
        return

    name = message.text.strip()

    if not name:
        await message.answer("Имя не может быть пустым")
        return

    await state.update_data(name=name)

    await message.answer(
        "Отлично 😄 Хотите добавить номер телефона?",
        reply_markup=kb.get_number
    )

    await state.set_state(CreateUserState.ask_number)

@router.message(CreateUserState.ask_number, F.contact)
async def accept_number(message: Message,
                        state: FSMContext,
                        us_sv: UserService,
                        ct_sv: CatalogService):
    # await callback.message.edit_reply_markup(reply_markup=None)  # ← убрали кнопки
    phone = message.contact.phone_number

    await message.answer("✅ Контакт получен")

    data = await state.get_data()
    name = data.get("name")
    tg_id = message.from_user.id

    try:
        ok = await us_sv.create_user(name, tg_id, phone)
    except Exception as e:
        await message.answer(f"❌ {e}\n\n что то пошло не так при вводе длительности услуги")
        return

    if ok:
        await message.answer(f"Отлично 😄 Теперь продолжим выбор услуги.")
        await show_catalogs(message, ct_sv)
    else:
        await message.answer(f"Что то пошло не так повторите попытку")

    await state.clear()

@router.message(F.text == "⏭ Пропустить", CreateUserState.ask_number)
async def reject_number(message: Message,
                        state: FSMContext,
                        us_sv: UserService,
                        ct_sv: CatalogService):
    await message.answer("Не проблема, продолжим без номера телефона!")

    data = await state.get_data()
    phone = "-"
    name = data.get("name")
    tg_id = message.from_user.id

    try:
        ok = await us_sv.create_user(name, tg_id, phone)
    except Exception as e:
        await message.answer(f"❌ {e}\n\n что то пошло не так при вводе длительности услуги")
        return

    if ok:
        await message.answer(f"Отлично 😄 Теперь продолжим выбор услуги.")
        await show_catalogs(message, ct_sv)
    else:
        await message.answer(f"Что то пошло не так повторите попытку")

    await state.clear()
