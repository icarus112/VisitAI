from decimal import Decimal

from pydantic import BaseModel, Field, model_validator, field_validator

class CatalogCreate(BaseModel):
    name: str = Field(..., max_length=127)
    price: Decimal
    duration: int

    @field_validator("price")
    def price_must_be_positive(cls, v: Decimal):
        if v <= 0:
            raise ValueError("Цена должна быть положительной")

        return v

    @field_validator("duration")
    def duration_is_positive(cls, v: int):
        if v < 0:
            raise ValueError("продолжительность обслуживания должно быть положительным")

        return v

    @field_validator("name")
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError("name can't be empty")

        return v

class CatalogResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    duration: int