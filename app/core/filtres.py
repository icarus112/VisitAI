from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.core.role import RoleCheck
from app.service.admin import AdminService
from app.core.conf import settings


class IsSuperAdmin(BaseFilter):

    async def __call__(self, message: Message, ad_sv: AdminService) -> bool:
        tg_id = message.from_user.id

        if settings.dev_mode:
            admin = await ad_sv.get_ad_by_tg_id(tg_id)

            if not admin:
                await message.answer("⛔ У тебя нет роли как админ")
                return False

            if not RoleCheck.is_super_admin(admin.role):
                await message.answer("⛔ нужны права супер админа")
                return False

            return True

        return  tg_id in settings.super_admins

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, ad_sv: AdminService) -> bool:
        # print("AD_RP =", ad_rp)
        tg_id = message.from_user.id
        admin = await ad_sv.get_ad_by_tg_id(tg_id)

        if settings.dev_mode:

            if not admin:
                await message.answer("⛔ У тебя нет роли как админ")
                return False

            if not RoleCheck.is_admin(admin.role):
                await message.answer("⛔ нужны права админа")
                return False

            return True

        if tg_id in settings.super_admins:
            return True

        if not admin:
            return False

        return RoleCheck.is_admin(admin.role)

