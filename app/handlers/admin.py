from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.service.admin import AdminService

router = Router()

@router.message(Command("setrole"))
async def set_role(message: Message,
                   ad_sv: AdminService):
    if not ad_sv.is_super_admin(tg_id=message.from_user.id):
        await message.answer("❌ Нет доступа")