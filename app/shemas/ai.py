from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


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
    date: str | None = None
    time: str | None = None
    comment: str | None = None

    user_problem: str | None = None
    recommended_queries: list[str] = [] # лист рекомендаций

    missing_fields: list[str] = [] #данные которые не хватают
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

    confidence: float = 0.0

