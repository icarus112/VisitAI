from enum import Enum, StrEnum


class BookStatus(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    WAITING_FOR_CAPTURE = "WAITING_FOR_CAPTURE"

class Role(StrEnum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    USER = "USER"