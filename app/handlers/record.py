from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.core import keyboards as kb
from app.core.states import CreateUserState
from app.service.catalog import CatalogService
from app.service.user import UserService

router = Router()

'''
========================================================================================
                                     ДОБАВИТЬ ЗАПИСЬ
========================================================================================
'''

@router.message(F.text == "✏️Добавить запись")
async def add_record(message: Message, state: FSMContext,
                     us_sv: UserService, ct_sv: CatalogService):

    user = await us_sv.get_by_tg_id(message.from_user.id)
    if not user:
        #  у юзера может не быть юзернейма
        name = message.from_user.username or message.from_user.first_name
        await state.update_data(suggested_name=name)

        await message.answer(f"Давайте познакомимся 😌\n\n"
                            f"Можно обращаться к вам как {name}?",
                             reply_markup=kb.authorization)
        await state.set_state(CreateUserState.ask_name)  # продолжение в файле handler/user.py
        return

    await show_catalogs(message, ct_sv)

async def show_catalogs(message: Message, ct_sv: CatalogService):
    catalogs = await ct_sv.get_all()

    await message.answer(
        "😌 Давайте выберем услугу",
        reply_markup=kb.catalog_keyboard(catalogs)
    )

@router.callback_query(F.data.startswith("catalog:"))
async def ct_select(callback: CallbackQuery,
                    ct_sv: CatalogService,
                    state: FSMContext):
    ct_id = int(callback.data.split(":")[1].strip())
    cts = await ct_sv.get_all()

    await callback.answer()

    for ct in cts:
        if ct.id == ct_id:
            selected = ct
            break

    if selected:
        await callback.message.edit_text(f"вы выбрали \n{selected.name} - "
                                         f"{selected.price} руб / {selected.duration} мин")
        await callback.message.answer("на какую дату вы бы хотели записаться:", reply_markup=kb.get_date)

        await state.update_data(user_tg_id=callback.from_user.id)
        await state.update_data(ct=selected.id)
        await state.set_state()
    else:
        await callback.message.edit_text("Услуга не найдена")

