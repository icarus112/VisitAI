from sqlalchemy import select

from database.models import Admin


class AdminRepos:
    def __init__(self, session):
        self.session = session

    async def is_admin(self, tg_id: int) -> bool:
        stmt = select(Admin).where(Admin.tg_id == tg_id)

        result = await (self.session.execute(stmt)
                        .scalar_one_or_none())

        if result is None:
            return False

        return True

    async def get_ad_by_id(self, tg_id: int) -> Admin:
        stmt = (select(Admin)
                .where(Admin.tg_id == tg_id))

        result = await self.session.execute(stmt)
        admin = result.scalar_one_or_none()
        return admin

    async def set_admin(self, tg_id: int):
        admin = Admin(
            tg_id=tg_id,
            role="ADMIN"
        )

        self.session.add(admin)

    async def change_role(self, tg_id: int, new_role: str):
        admin = await self.get_ad_by_id(tg_id)

        if admin:
            admin.role = new_role
        else:
            admin = Admin(tg_id=tg_id, role=new_role)
            self.session.add(admin)

        return admin