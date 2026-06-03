from app.shemas.record import UserCreate
from database.models import User
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
            logging.info(f"Created user: id={created_user.id}, name={created_user.name}, tg_id={created_user.tg_id}")

        except Exception:
            logger.exception(
                f"Failed to create user tg_id={tg_id}"
            )
            return False