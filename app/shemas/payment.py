from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class PaymentCreate(BaseModel):
    booking_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, decimal_places=2)
    description: str

    @field_validator("description")
    def description_not_empty(cls, v: str) -> str:
        check = v.strip()

        if not check:
            raise ValueError("description can't be empty")

        return v