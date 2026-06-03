import datetime
import logging

from app.core import enum
from logs import logger
from app.shemas.record import BookingCreate, BookingRequestResult
from database.models import Booking

logger = logging.getLogger(__name__)
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
            logger.warning(f"user is not found for creating booking, user tg_id={tg_id}")
            raise ValueError("Пользователь не найден в sv")

        ct = await self.ct_rp.get_ct_by_id(ct_id)
        if not ct:
            logger.warning(f"ct is not found for creating booking, ct id={ct_id}")
            raise ValueError("Услуга не найдена в sv")

        if isinstance(date_str, datetime.date):
            booking_date = date_str
        elif isinstance(date_str, str):
            booking_date = self.parse_date(date_str)
        else:
            logger.warning("wrong date format for creating booking, date_str= ", date_str)
            raise ValueError("Неверный тип даты в sv")
        parsed_time = self.parse_time(time_str)

        booking = BookingCreate(
            user_id=user.id,
            catalog_id=ct_id,
            date=booking_date,
            time=parsed_time,
            status=enum.BookStatus.PENDING,
            comment=comment
        )
        try:
            new_booking = await self.bk_rp.create_booking(booking)
        except Exception as e:
            logger.exception("database error while creating booking")
            raise

        logger.info(f"forwarded new booking={ct.name}, ct_id:{ct.id} by user={user.id} to admin ")

        return BookingRequestResult(
            booking=new_booking,
            user=user,
            ct=ct,
            comment=comment
        )

    def parse_date(self, date_str: str) -> datetime.date:
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
            logging.warning(f"can't parse date for creating booking , date_str= {date_str}")
            raise ValueError("Неверный формат даты в sv")

        try:
            return datetime.datetime.strptime(new_wd, "%Y.%m.%d").date()
        except ValueError:
            logging.warning(f"can't parse date for creating booking , date_str= {date_str}")
            raise ValueError("Ошибка при переводе даты в sv")

    def parse_time(self, time_str: str) -> datetime.time:
        time_str = time_str.strip().replace(" ", ":")

        try:
            return datetime.time.fromisoformat(time_str)
        except ValueError:
            logger.warning(f"wrong time format for creating booking, time_str= {time_str}")
            raise ValueError("Ошибка при переводе времени в sv")

    async def get_booking(self, booking_id: int) -> Booking | None:

        try:
            booking = await self.bk_rp.get_booking(booking_id)

        except Exception:
            logger.exception(
                f"Failed to get booking "
                f"booking_id={booking_id}"
            )
            raise

        if booking is None:
            logger.warning(
                f"booking not found "
                f"booking_id={booking_id}"
            )

        return booking

    async def cancel_pay(self, booking_id: int):
        booking = await self.bk_rp.get_booking(booking_id)

        if booking is None:
            raise ValueError(f"Booking {booking_id} not found")

        rowcount = await self.bk_rp.cancel_pay(booking_id)

        if rowcount == 0:
            raise RuntimeError(f"Booking {booking_id} was not updated")

        logger.info(
            "booking cancelled without online payment, booking_id=%s",
            booking_id,
        )


