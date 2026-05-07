import datetime
from datetime import time

from app.core import enum
from app.shemas.record import BookingCreate, BookingRequestResult
from database.models import User, Booking


class BookingService:
    def __init__(self, bk_rp, us_rp, ct_rp):
        self.bk_rp = bk_rp
        self.us_rp = us_rp
        self.ct_rp = ct_rp

    def today(self) -> datetime.date:
        return datetime.date.today()

    async def create_booking(self,
                             tg_id: int,
                             ct_id: int,
                             date_str: str | datetime.date,
                             time_str: str,
                             comment: str) -> BookingRequestResult:
        user = await self.us_rp.get_by_tg_id(tg_id)
        if not user:
            raise ValueError("Пользователь не найден в sv")

        ct = await self.ct_rp.get_ct_by_id(ct_id)
        if not ct:
            raise ValueError("Услуга не найдена в sv")

        if isinstance(date_str, datetime.date):
            booking_date = date_str
        elif isinstance(date_str, str):
            booking_date = self._parse_date(date_str)
        else:
            raise ValueError("Неверный тип даты в sv")
        parsed_time = self._parse_time(time_str)

        booking = BookingCreate(
            user_id=user.id,
            catalog_id=ct_id,
            date=booking_date,
            time=parsed_time,
            status=enum.BookStatus.PENDING,
            comment=comment
        )

        new_booking = await self.bk_rp.create_booking(booking)

        return BookingRequestResult(
            booking=new_booking,
            user=user,
            ct=ct,
            comment=comment
        )

    def _parse_date(self, date_str: str) -> datetime.date:
        wd = date_str.split(".")
        wd = [el for el in wd if el != ""]

        month = datetime.date.today().month
        year = datetime.date.today().year

        if len(wd) == 1:
            new_wd = f"{year}.{month}.{wd[0]}"
        elif len(wd) == 2:
            new_wd = f"{year}.{wd[1]}.{wd[0]}"
        elif len(wd) == 3:
            new_wd = f"{wd[2]}.{wd[1]}.{wd[0]}"
        else:
            raise ValueError("Неверный формат даты в sv")

        try:
            return datetime.datetime.strptime(new_wd, "%Y.%m.%d").date()
        except ValueError:
            raise ValueError("Ошибка при переводе даты в sv")

    def _parse_time(self, time_str: str) -> datetime.time:
        time_str = time_str.strip().replace(" ", ":")

        try:
            return datetime.time.fromisoformat(time_str)
        except ValueError:
            raise ValueError("Ошибка при переводе времени в sv")

    async def get_booking(self, booking_id: int) -> Booking:
        try:
            booking = await self.bk_rp.get_booking(booking_id)
        except ValueError:
            raise ValueError("Не удалось получить booking by id в sv")

        return booking



