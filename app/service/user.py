from app.shemas.record import UserCreate
from database.models import User

class UserService:
    def __init__(self, us_rp):
        self.us_rp = us_rp

    async def get_by_tg_id(self, tg_id: int) -> User:
        return await self.us_rp.get_by_tg_id(tg_id)

    async def create_user(self, name,tg_id, phone) -> bool:
        try:
            user = UserCreate(name=name,
                              tg_id=tg_id,
                              phone=phone)

            user= await self.us_rp.create_user(user)
            if user:
                return True

            return False
        except Exception:
            return False

