from aiogram.types import Message

from app.core.enum import Role
from conf import SUPER_ADMINS, DEV_MODE
from database.models import Admin


# def is_super_admin(tg_id: int) -> bool:
#     return tg_id in SUPER_ADMINS

class AdminService:
    def __init__(self, ad_rp):
        self.ad_rp = ad_rp

    def is_super_admin(self, tg_id: int) -> bool:
        return tg_id in SUPER_ADMINS

    async def is_admin(self, tg_id: int) -> bool:
        return self.ad_rp.is_admin(tg_id)

    async def set_admin(self, tg_id: int) -> bool:
        try:
            await self.ad_rp.set_admin(tg_id)
            return True
        except Exception:
            return False

    async def get_ad_by_id(self, tg_id: int) -> Admin | None:
        try:
            return await self.ad_rp.get_ad_by_id(tg_id)
        except Exception:
            return None

    async def change_role(self, tg_id: int, new_role: str) -> Role:
        if not DEV_MODE:
            raise PermissionError("⛔ команда не доступна")

        try:
            role = Role(new_role.upper())
        except Exception:
            raise ValueError("Такой роли нет")

        await self.ad_rp.change_role(tg_id=tg_id,
                                     new_role=role.value)

        return role
