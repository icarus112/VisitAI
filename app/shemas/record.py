from pydantic import BaseModel


class UserCreate(BaseModel):
    tg_id: int
    name: str
    number: int