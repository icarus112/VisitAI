from enum import Enum, StrEnum


class BookStatus(Enum):
    PENDING = "PENDING" #ожидание пока админ согласует
    PAID = "PAID" #согласовано, оплачено
    UNPAID = "UNPAID" #согласовано, не оплачено
    CANCELLED = "CANCELLED" #Отменено
    COMPLETED = "COMPLETED" #услуга оказана, заявка закрыта
    NO_SHOW = "NO_SHOW" #не пришел
    FAILED_PAY = "FAILED_PAY" #ошибка при оплате

class Role(StrEnum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    USER = "USER"