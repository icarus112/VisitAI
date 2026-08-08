from app.shemas.record import UserCreate
from app.database.models import User
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, us_rp):
        self.us_rp = us_rp

    async def get_by_tg_id(self, tg_id: int) -> User:
        return await self.us_rp.get_by_tg_id(tg_id)

    async def create_user(self, name,tg_id, phone) -> None:
        try:
            user = UserCreate(name=name,
                              tg_id=tg_id,
                              phone=phone)

            created_user= await self.us_rp.create_user(user)
            logger.info(
                "Created user successfully: id=%r, name=%r, tg_id=%r",
                created_user.id,
                created_user.name,
                created_user.tg_id,
            )
        except Exception:
            logger.exception(
                "Service failed to create user: name=%r, tg_id=%r, phone=%r",
                name,
                tg_id,
                phone,
            )
            raise