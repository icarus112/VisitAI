from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class PaymentCreate(BaseModel):
    booking_id: int
    amount: Decimal = Field(gt=0, decimal_places=2)
    description: str

    @field_validator("booking_id")
    def booking_id_is_positive(cls, v: int):
        if v < 0:
            raise ValueError("booking_id должно быть положительным")

        return v

    @field_validator("description")
    def description_not_empty(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError("description can't be empty")

        return v

    @field_validator("amount")
    def amount_must_be_positive(cls, v: Decimal):
        if v <= 0:
            raise ValueError("Цена должна быть положительной")

        return v