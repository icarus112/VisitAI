from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.service.admin import AdminService
from conf import DEV_MODE

dev_router = Router()

@dev_router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Действие отменено")

#Only for dev test!!
@dev_router.message(Command("change_role"))
async def change_role(message: Message, ad_sv: AdminService, state: FSMContext):
    await state.clear()

    if not DEV_MODE:
        await message.answer("⛔ команда не доступна")
        return

    await message.answer("#DEV_MODE")

    parts = message.text.split()
    #разделяем сообщение на parts by " "

    if len(parts) != 2:
        await message.answer("Формат: /change_role <role>\n\n"
            "Роли: super_admin, admin, user"
        )
        return


    try:
        role = await ad_sv.change_role(
            tg_id=message.from_user.id,
            new_role = parts[1].upper()
        )
    except ValueError :
        await message.answer(
            "❌ Такой роли нет.\n"
            "Доступные роли: SUPER_ADMIN, ADMIN, USER")
        return

    await message.answer(f"✅ DEV-роль изменена на: {role.value}")