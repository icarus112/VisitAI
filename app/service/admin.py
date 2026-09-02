import logging
from app.core.enum import AdminRole
from app.core.conf import settings
from app.database.models import Admin

logger = logging.getLogger(__name__)

# def is_super_admin(tg_id: int) -> bool:
#     return tg_id in SUPER_ADMINS

class AdminService:
    def __init__(self, ad_rp):
        self.ad_rp = ad_rp

    def is_super_admin(self, tg_id: int) -> bool:
        return tg_id in settings.super_admins

    async def is_admin(self, tg_id: int) -> bool:
        return await self.ad_rp.is_admin(tg_id)

    async def create_admin(self, tg_id, name: str) -> None:
        await self.ad_rp.create_admin(tg_id, name)
        logger.info(f"admin={name}, tg_id= {tg_id} get admin rights")

    async def get_ad_by_tg_id(self, tg_id: int) -> Admin | None:
        try:
            return await self.ad_rp.get_ad_by_tg_id(tg_id)
        except Exception:
            logger.warning(f"can't get admin by tg_id, [tg_id={tg_id}]")
            return None

    async def get_ad_by_id(self, id: int) -> Admin | None:
        try:
            return await self.ad_rp.get_ad_by_id(id)
        except Exception:
            logger.warning(f"can't get admin by id, [id={id}]")
            return None

    async def change_role(self, tg_id: int, new_role: str) -> AdminRole:
        admin = await self.get_ad_by_tg_id(tg_id)
        if admin is None:
            raise ValueError("format_admin() expected Admin got None")

        if not settings.dev_mode:
            raise PermissionError("⛔ команда не доступна")

        try:
            role = AdminRole(new_role.upper())
        except Exception:
            raise ValueError("Такой роли нет")

        await self.ad_rp.change_role(tg_id=tg_id,
                                     new_role=role)

        return role

    async def get_all_admin(self) -> list[Admin]:
        admins = await self.ad_rp.get_all_admin()
        return admins

    def format_admin(self, admin: Admin) -> str:
        if admin is None:
            raise ValueError("format_admin() expected Admin got None")

        return (
            f"👤 Имя: {admin.name}\n"
            f"🆔 TG ID: {admin.tg_id}\n"
            f"🪪 Должность: {admin.role}\n"
        )

    async def get_info(self) -> str:
        text = "Список ваших сотрудников\n\n"
        admins = await self.get_all_admin()
        if admins:
            lines = [self.format_admin(admin) for admin in admins]
            text += "<pre>\n" + "\n".join(lines) + "\n</pre>\n"

            return text

        else:
            return "Список пуст, сотрудников нету"

    async def remove_admin_by_id(self, id: int) -> Admin | None:
        admin = await self.ad_rp.remove_admin_by_id(id)
        if admin is None:
            logger.warning(f"can't get admin by admin_id={id} ")
            return None

        logger.info(f"admin_id={id} is removed")
        return admin