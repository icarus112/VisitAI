from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class AIIntentBooking(BaseModel):
    intent: Literal[
        "create_booking",
        "check_booking",
        "cancel_booking",
        "recommend_catalog",
        "faq",
        "unknown"
    ]

    catalog_query: str | None = None
    search_keywords: list[str] = Field(default_factory=list)

    date: str | None = None
    time: str | None = None
    comment: str | None = None

    user_problem: str | None = None
    recommended_queries: list[str] = [] # лист рекомендаций

    missing_fields: list[str] = Field(default_factory=list) #данные которые не хватают
    confidence: float = 0.0

class AIIntentCatalog(BaseModel):
    intent: Literal[
        "create_catalog",
        "check_catalog",
        "edit_price",
        "edit_duration",
        "unknown"
    ]

    name: str | None = None
    price: Decimal | None = None
    duration: int | None = None

    missing_fields: list[str] = []  # данные которые не хватают
    confidence: float = 0.0

class AICatalogDescription(BaseModel):
    description: str = Field(min_length=5, max_length=500)
    keywords: list[str] = Field(default_factory=list, max_length=10)
    client_phrases: list[str] = Field(default_factory=list, max_length=7)
