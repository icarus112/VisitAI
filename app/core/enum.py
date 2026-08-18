from enum import Enum, StrEnum


class BookStatus(StrEnum):
    PENDING = "PENDING" #ожидание пока админ согласует
    CONFIRMED = "CONFIRMED" #администратор согласовал
    CANCELLED = "CANCELLED" # отменено
    COMPLETED = "COMPLETED" # услуга оказана
    NO_SHOW = "NO_SHOW" # клиент не пришел
    REMOVED = "REMOVED" #удалена пользователем

class PaymentMethod(StrEnum):
    PENDING = "PENDING"
    ONLINE = "ONLINE"
    ON_SITE = "ON_SITE"

class PaymentStatus(StrEnum):
    UNPAID = "UNPAID"
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED" # возврат средств

class Role(StrEnum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    USER = "USER"