from sqlalchemy import select

from app.core.enum import AdminRole
from app.database.models import Admin


class AdminRepos:
    def __init__(self, session):
        self.session = session

    async def is_admin(self, tg_id: int) -> bool:
        stmt = select(Admin).where(Admin.tg_id == tg_id)

        result = await self.session.execute(stmt)
        is_admin = result.scalar_one_or_none()

        if is_admin is None:
            return False

        return True

    async def get_ad_by_tg_id(self, tg_id: int) -> Admin | None:
        stmt = (select(Admin)
                .where(Admin.tg_id == tg_id))

        result = await self.session.execute(stmt)
        admin = result.scalar_one_or_none()
        return admin

    async def get_ad_by_id(self, id: int) -> Admin | None:
        stmt = (select(Admin)
                .where(Admin.id == id))

        result = await self.session.execute(stmt)
        admin = result.scalar_one_or_none()
        return admin

    async def create_admin(self, tg_id: int, name: str):
        admin = Admin(
            tg_id=tg_id,
            role="ADMIN",
            name=name
        )
        self.session.add(admin)
        await self.session.flush()
        return admin

    async def get_all_admin(self) -> list[Admin]:
        stmt = (select(Admin).order_by(Admin.id))
        results = await self.session.execute(stmt)
        admins = results.scalars().all()
        return admins

    async def change_role(self, tg_id: int, new_role: AdminRole) -> Admin:
        admin = await self.get_ad_by_tg_id(tg_id)

        if admin:
            admin.role = new_role
        else:
            raise ValueError(f"cant get admin by tg_id for change_role admin, ad_tg_id= {tg_id}")

        return admin

    async def remove_admin_by_id(self, id: int) -> bool:
        admin = await self.get_ad_by_id(id)

        if admin is None:
            raise ValueError (f"cant get admin by id for removing admin, ad_id= {id}")

        await self.session.delete(admin)
        return True