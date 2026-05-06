import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator, ConfigDict
from app.core.enum import BookStatus
from database.models import User, Catalog


class UserCreate(BaseModel):
    tg_id: int
    name: str
    phone: str

    @field_validator("tg_id")
    def tg_id_is_positive(cls, v: int):
        if v < 0:
            raise ValueError("tg_id должно быть положительным")

        return v

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

class UserRead(BaseModel):
    id: int
    tg_id: int
    name: str
    phone: str

    model_config = ConfigDict(from_attributes=True)

class CatalogRead(BaseModel):
    id: int
    name: str
    price: Decimal
    duration: int

    model_config = ConfigDict(from_attributes=True)

class BookingRead(BaseModel):
    user_id: int
    ct_id: int
    date: datetime.date
    time: datetime.time
    status: BookStatus
    comment: str

    model_config = ConfigDict(from_attributes=True)


# class RequestCreate(BaseModel):
#     user: UserRead
#     ct: CatalogRead
#     phone: str
#     date: str
#     time: str
#     comment: str
#
#     model_config = {"from_attributes": True}
#
#     @field_validator("phone")
#     def phone_not_empty(cls, v: str) -> str:
#         v = v.strip()
#
#         if not v:
#             raise ValueError("phone number can't be empty")
#
#         return v
#
#     @field_validator("date")
#     def date_not_empty(cls, v: str) -> str:
#         v = v.strip()
#
#         if not v:
#             raise ValueError("date can't be empty")
#
#         return v
#
#     @field_validator("time")
#     def time_not_empty(cls, v: str) -> str:
#         v = v.strip()
#
#         if not v:
#             raise ValueError("time can't be empty")
#
#         return v
#
#     @field_validator("comment")
#     def comment_not_empty(cls, v: str) -> str:
#         v = v.strip()
#
#         if not v:
#             raise ValueError("comment can't be empty")
#
#         return v

class BookingCreate(BaseModel):
    user_id: int
    catalog_id: int
    date: datetime.date
    time: datetime.time
    status: BookStatus
    comment: str

    model_config = {"from_attributes": True}

    @field_validator("user_id")
    def user_id_is_positive(cls, v: int):
        if v < 0:
            raise ValueError("user_id должно быть положительным")

        return v

    @field_validator("catalog_id")
    def catalog_id_is_positive(cls, v: int):
        if v < 0:
            raise ValueError("catalog_id должно быть положительным")

        return v

class BookingRequestResult(BaseModel):
    booking: BookingRead
    user: UserRead
    ct: CatalogRead
    comment: str



