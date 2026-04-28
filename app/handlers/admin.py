from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.core import keyboards as kb
from app.core.States import AdminState
from app.core.filtres import IsSuperAdmin, IsAdmin
from app.service.admin import AdminService
from conf import DEV_MODE

router = Router()

@router.message(Command("admin"), IsAdmin())
async def admin_panel(message: Message):
    await message.answer("✅ Доступ открыт", reply_markup=kb.admin)


@router.message(F.text == "🪪 Добавить администратора", IsSuperAdmin())
async def get_admin_id(message: Message, state: FSMContext):
    await message.answer("введите пожалуйста ID будущего сотрудника: ")
    await message.answer("если не знаете как получить свой id "
                         "зайдите в поисковую строку и введите @getmyid_bot"
                         "\nдальше нажмите на Start или введите /start"
                         "\n\nтаким образом вы должны получить свой tg id")
    await state.set_state(AdminState.get_id)

@router.message(AdminState.get_id)
async def set_admin(message: Message,
                    state: FSMContext,
                    ad_sv: AdminService):
    if not message.text.isdigit():
        await message.answer("ID должно быть числом и без знаков")
        return

    tg_id = int(message.text)

    admin = await ad_sv.get_ad_by_id(tg_id)
    if not admin:
        ok = await ad_sv.set_admin(tg_id)
        if not ok:
            await message.answer("произошла ошибка! повторите попытку")
            return

        await message.answer("✅ Админ добавлен")
        await state.clear()
        return

    await message.answer("!Админ с таким id уже существует")

