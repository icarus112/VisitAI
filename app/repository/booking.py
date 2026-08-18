from datetime import datetime, timedelta

from sqlalchemy import select, update, func, delete, and_
from sqlalchemy.orm import joinedload

from app.core.enum import BookStatus
from app.shemas.record import BookingCreate
from app.database.models import Booking

ACTIVE_BOOKING_STATUSES = (
    BookStatus.PENDING,
    BookStatus.CONFIRMED,
)

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

    async def get_my_bookings(self, us_id: int) -> list[Booking]:
        stmt = (
            select(Booking)
            .where(
                Booking.user_id == us_id,
                Booking.status.in_(ACTIVE_BOOKING_STATUSES),
            )
            .order_by(Booking.scheduled_at, Booking.id)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    async def count_my_bk(self, user_id) -> int:
        stmt = (
            select(func.count(Booking.id))
            .where
                (
            Booking.status.in_(ACTIVE_BOOKING_STATUSES),
            Booking.user_id == user_id,
                )
        )

        result = await self.session.execute(stmt)

        return result.scalar_one()

    async def get_bk_page(self, page: int, user_id: int) -> Booking | None:
        stmt = (
            select(Booking)
            .where(
                Booking.status.in_(ACTIVE_BOOKING_STATUSES),
                Booking.user_id == user_id
            )
            .order_by(Booking.scheduled_at, Booking.id)
            .limit(1)
            .offset(page)
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()


    async def auto_complete_old(self, us_id: int) -> int:
        threshold = datetime.now() - timedelta(hours=3)

        stmt = (
            update(Booking)
                .where(
                    Booking.user_id == us_id,
                    Booking.status.in_(
                        ACTIVE_BOOKING_STATUSES),
                        Booking.scheduled_at < threshold
                    )

                .values(status=BookStatus.COMPLETED)
                )

        result = await self.session.execute(stmt)
        return result.rowcount

    async def cancel_pay(self, booking_id: int):
        stmt = (update(Booking)
                .where(Booking.id == booking_id)
                .values(status=BookStatus.CONFIRMED))

        result = await self.session.execute(stmt)

        return result.rowcount

    async def remove_bk(self, bk_id: int):

        stmt = (update(Booking)
                .where(Booking.id == bk_id)
                .values(status=BookStatus.REMOVED))

        result = await self.session.execute(stmt)
        return result.rowcount