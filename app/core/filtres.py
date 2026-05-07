from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.core.role import RoleCheck
from app.service.admin import AdminService
from conf import SUPER_ADMINS, DEV_MODE


class IsSuperAdmin(BaseFilter):

    async def __call__(self, message: Message, ad_sv: AdminService) -> bool:
        tg_id = message.from_user.id

        if DEV_MODE:
            admin = await ad_sv.get_ad_by_tg_id(tg_id)

            if not admin:
                await message.answer("⛔ У тебя нет роли как админ")
                return False

            if not RoleCheck.is_super_admin(admin.role):
                await message.answer("⛔ нужны права супер админа")
                return False

            return True

        return  tg_id in SUPER_ADMINS

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message, ad_sv: AdminService) -> bool:
        # print("AD_RP =", ad_rp)
        tg_id = message.from_user.id
        admin = await ad_sv.get_ad_by_tg_id(tg_id)

        if DEV_MODE:

            if not admin:
                await message.answer("⛔ У тебя нет роли как админ")
                return False

            if not RoleCheck.is_admin(admin.role):
                await message.answer("⛔ нужны права админа")
                return False

            return True

        if tg_id in SUPER_ADMINS:
            return True

        if not admin:
            return False

        return RoleCheck.is_admin(admin.role)

