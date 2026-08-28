from decimal import Decimal

from pydantic import BaseModel, Field, model_validator, field_validator, ConfigDict


class CatalogCreate(BaseModel):
    name: str = Field(..., max_length=127)
    price: Decimal = Field(gt=0)
    duration: int = Field(gt=0)

    description: str
    keywords: list[str] = Field(default_factory=list)
    client_phrases: list[str] = Field(default_factory=list)

    def to_list(self) -> list:
        return [self.name, self.price, self.duration, self.description, self.keywords, self.client_phrases]

    @field_validator("name")
    def name_not_empty(cls, v: str) -> str:
        check = v.strip()

        if not check:
            raise ValueError("name can't be empty")

        return v

    @field_validator("description")
    def description_not_empty(cls, v: str) -> str:
        check = v.strip()

        if not check:
            raise ValueError("description can't be empty")

        return v

# class CatalogResponse(BaseModel):
#     id: int
#     name: str
#     price: Decimal
#     duration: int
#
#     description: str
#     keywords: list[str] = Field(default_factory=list)
#     client_phrases: list[str] = Field(default_factory=list)
#
#     model_config = ConfigDict(from_attributes=True)

class CatalogList(BaseModel):
    item: list[CatalogCreate]

    def __iter__(self):
        return iter(self.item)