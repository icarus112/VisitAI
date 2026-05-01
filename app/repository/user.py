from sqlalchemy import select
from sqlalchemy.engine import result

from app.shemas.record import UserCreate
from database.models import User


class UserRepos:
    def __init__(self, session):
        self.session = session

    async def get_by_tg_id(self, tg_id) -> User|None:
        stmt = (select(User)
                .where(User.tg_id == tg_id))

        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def create_user(self, user_py: UserCreate) -> User:
        user = User(** user_py.model_dump())

        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        return user

