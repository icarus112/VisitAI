from functools import lru_cache
from app.database.async_engine import async_session
from app.core.conf import settings
from app.repository.booking import BookingRepos

from app.service.payment import PaymentService

# lru_cache - Если функция вызывается повторно с теми же аргументами, она не вычисляется заново,
# а мгновенно возвращает готовый результат из кэша.
@lru_cache
async def get_payment_service() -> PaymentService:
    async with async_session() as session:
        bk_rp = BookingRepos(session)

    return PaymentService(return_url=settings.payment_return_url,
                          bk_rp=bk_rp)