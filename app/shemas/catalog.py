from decimal import Decimal

from pydantic import BaseModel, Field, model_validator, field_validator, ConfigDict


class CatalogCreate(BaseModel):
    name: str = Field(..., max_length=127)
    price: Decimal
    duration: int

    description: str
    keywords: list[str] = Field(default_factory=list)
    client_phrases: list[str] = Field(default_factory=list)

    def to_list(self) -> list:
        return [self.name, self.price, self.duration]

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

    description: str
    keywords: list[str] = Field(default_factory=list)
    client_phrases: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class CatalogList(BaseModel):
    item: list[CatalogCreate]

    def __iter__(self):
        return iter(self.item)