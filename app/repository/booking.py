from sqlalchemy import select, update

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

    async def cancel_pay(self, booking_id: int):
        stmt = (update(Booking)
                .where(Booking.id == booking_id)
                .values(status=BookStatus.CANCELLED))

        result = await self.session.execute(stmt)

        return result.rowcount