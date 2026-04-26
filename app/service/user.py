from database.models import User

class UserService:
    def __init__(self, us_rp):
        self.us_rp = us_rp

    async def get_by_tg_id(self, tg_id: int) -> User:
        return await self.us_rp.get_by_tg_id(tg_id)