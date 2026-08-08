from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator, ConfigDict, Field
from app.core.enum import BookStatus, PaymentMethod

class UserCreate(BaseModel):
    tg_id: int = Field(gt=0)
    name: str
    phone: str

    @field_validator("name")
    def name_not_empty(cls, v: str) -> str:
        check = v.strip()

        if not check:
            raise ValueError("name can't be empty")

        return v

    @field_validator("phone")
    def phone_not_empty(cls, v: str) -> str:
        check = v.strip()

        if not check:
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
    id: int
    user_id: int
    catalog_id: int
    scheduled_at: datetime
    status: BookStatus
    comment: str

    model_config = ConfigDict(from_attributes=True)

class BookingCreate(BaseModel):
    user_id: int = Field(gt=0)
    catalog_id: int = Field(gt=0)
    scheduled_at: datetime
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    booking_status: BookStatus = Field(default=BookStatus.PENDING)
    payment_method: PaymentMethod = Field(default=PaymentMethod.PENDING)
    comment: str | None = None

    model_config = {"from_attributes": True}

class BookingList(BaseModel):
    item: list[BookingCreate]

class BookingRequestResult(BaseModel):
    booking: BookingRead
    user: UserRead
    ct: CatalogRead
    comment: str



