from datetime import datetime, timedelta
from typing import List

from sqlalchemy import select, update, and_, or_, func, delete
from sqlalchemy.orm import joinedload

from app.core.enum import BookStatus, PaymentMethod
from app.shemas.record import BookingCreate
from app.database.models import Booking


class BookingRepos:
    def __init__(self, session):
        self.session = session

    async def create_booking(self,new_booking: BookingCreate) -> Booking:
        booking = Booking(**new_booking.model_dump())
        self.session.add(booking)
        await self.session.flush()
        await self.session.refresh(booking)

        return booking

    async def get_booking(self, booking_id: int) -> Booking:
        stmt = (select(Booking)
                .where(Booking.id == booking_id))

        result = await self.session.execute(stmt)
        booking = result.scalar_one_or_none()

        return booking

    async def get_full_bk(self, bk_id: int):
        stmt = (select(Booking)
                .options(
                joinedload(Booking.user),
                joinedload(Booking.catalog)
                )
                .where(Booking.id == bk_id))

        result = await self.session.execute(stmt)
        booking = result.scalar_one_or_none()

        return booking

    async def get_my_bookings(self, us_id: int) -> List[Booking]:
        stmt = (select(Booking)
                .where(and_(Booking.user_id == us_id,
                       Booking.status.in_([BookStatus.PENDING, BookStatus.UNPAID,
                                           BookStatus.PAID, BookStatus.FAILED_PAY])))
                .order_by(Booking.date, Booking.time))
        result = await self.session.execute(stmt)
        bookings = result.scalars().all()
        return bookings

    async def count_bk(self) -> int:
        stmt = (select(func.count(Booking.id))
                .where(Booking.status.in_([BookStatus.PENDING, BookStatus.UNPAID,
                                           BookStatus.PAID, BookStatus.FAILED_PAY]))
                )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_bk_page(self, page: int) -> Booking:

        stmt = (select(Booking)
                .where(Booking.status.in_([BookStatus.PENDING, BookStatus.UNPAID,
                                                BookStatus.PAID, BookStatus.FAILED_PAY]))
                .order_by(Booking.id)
                .limit(1)
                .offset(page))

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def auto_complete_old(self, us_id: int) -> None:
        threshold = datetime.now() - timedelta(hours=3)

        stmt = (
            update(Booking)
                .where(and_(Booking.user_id == us_id,
                            Booking.status.in_([
                                BookStatus.UNPAID,
                                BookStatus.PAID,
                                BookStatus.FAILED_PAY]),
                            or_(
                                Booking.date < threshold.date(),
                                and_(
                                    Booking.date == threshold.date(),
                                    Booking.time < threshold.time()
                                            )
                                )
                            )
                       )
                .values(status=BookStatus.COMPLETED))

        result = await self.session.execute(stmt)
        return result.rowcount

    async def cancel_pay(self, booking_id: int):
        stmt = (update(Booking)
                .where(Booking.id == booking_id)
                .values(status=BookStatus.UNPAID))

        result = await self.session.execute(stmt)

        return result.rowcount

    async def remove_bk(self, bk_id: int):

        stmt = (delete(Booking)
                .where(Booking.id == bk_id))

        result = await self.session.execute(stmt)
        return result.rowcount