from pydantic import BaseModel, field_validator


class UserCreate(BaseModel):
    tg_id: int
    name: str
    phone: str

    @field_validator("name")
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError("name can't be empty")

        return v

    @field_validator("phone")
    def phone_not_empty(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError("phone number can't be empty")

        return v

