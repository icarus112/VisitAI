from datetime import datetime, timedelta
from typing import List

from sqlalchemy import select, update, and_, or_

from app.core.enum import BookStatus
from app.shemas.record import BookingCreate
from database.models import Booking


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

    async def get_my_bookings(self, us_id: int) -> List[Booking]:
        stmt = (select(Booking)
                .where(and_(Booking.user_id == us_id,
                       Booking.status.in_([BookStatus.PENDING.value, BookStatus.UNPAID.value,
                                           BookStatus.PAID.value, BookStatus.FAILED_PAY.value])))
                .order_by(Booking.date, Booking.time))
        result = await self.session.execute(stmt)
        bookings = result.scalars().all()
        return bookings

    async def auto_complete_old(self, us_id: int) -> None:
        threshold = datetime.now() - timedelta(hours=3)

        stmt = (
            update(Booking)
                .where(and_(Booking.user_id == us_id,
                            Booking.status.in_([
                                BookStatus.UNPAID.value,
                                BookStatus.PAID.value,
                                BookStatus.FAILED_PAY.value]),
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