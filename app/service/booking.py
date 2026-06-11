import datetime
import logging

from logs import logger
from app.shemas.record import BookingCreate, BookingRequestResult
from database.models import Booking
from app.core.enum import BookStatus

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
        ct = await self.ct_rp.get_ct_by_id(ct_id)
        active_field = datetime.datetime.now()

        if not user:
            logger.warning(f"user is not found for creating booking, user tg_id={tg_id}")
            raise ValueError("Пользователь не найден в sv")

        if not ct:
            logger.warning(f"ct is not found for creating booking, ct id={ct_id}")
            raise ValueError("Услуга не найдена в sv")

        if isinstance(date_str, datetime.date):#если date_str принадлежит к datetime.date
            booking_date = date_str
        elif isinstance(date_str, str):#если date_str принадлежит к str
            booking_date = self.parse_date(date_str)
        else:
            logger.warning("wrong date format for creating booking, date_str= ", date_str)
            raise ValueError("Неверный тип даты в sv")
        parsed_time = self.parse_time(time_str)

        if booking_date < active_field.date() and parsed_time < active_field.time():
            logger.warning("booking is rejected cause of wrong date/time:"
                           f"date:{date_str}, time:{parsed_time}")
            raise ValueError("Дата и время не должно быть в прошлом времени")

        booking = BookingCreate(
            user_id=user.id,
            catalog_id=ct_id,
            date=booking_date,
            time=parsed_time,
            status=BookStatus.PENDING,
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
            "booking received without online payment, booking_id=%s",
            booking_id,
        )

    async def my_bk_info(self, us_id: int) -> str:
        await self.bk_rp.auto_complete_old(us_id)

        text = "Ваши созданные заявки:"
        my_bks = await self.bk_rp.get_my_bookings(us_id)
        lines = []
        if not my_bks:
            return "Список пуст, услуг на данный момент не обнаружена"
        else:
            for bk in my_bks:
                ct = await self.ct_rp.get_ct_by_id(bk.catalog_id)
                tran_status = await self.trans_pay_status(bk.status)
                lines.append("\n\n______________________________")
                lines.append(f"\nУслуга: {ct.name}")
                lines.append(f"Дата: {bk.date.strftime('%Y.%m.%d')}")
                lines.append(f"Время: {bk.time}")
                lines.append(f"Статус: {tran_status}")

            text += "\n".join(lines)
            return text

    async def trans_pay_status(self, status: BookStatus) -> str:
        if status == BookStatus.PENDING:
            return "Ожидание ответа"
        elif status == BookStatus.UNPAID:
            return "Принято, не оплачено"
        elif status == BookStatus.PAID:
            return "Принято, оплачено"
        elif status == BookStatus.FAILED_PAY:
            return "Ошибка при оплате"
        else:
            raise ValueError(f"Ошибка при переводе trans_pay_status для статуса: %s", status)
            logger.warning("trans_pay_status failed for status: %s", status)


                    # id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
                    # user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
                    # catalog_id: Mapped[int] = mapped_column(ForeignKey("catalogs.id"), nullable=False)
                    # date: Mapped[date] = mapped_column(Date, nullable=False)
                    # time: Mapped[time] = mapped_column(Time, nullable=False)
                    # status: Mapped[BookStatus] = mapped_column(Enum(BookStatus), default=enum.BookStatus.PENDING,
                    #                                            nullable=False)
                    # payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
                    # comment: Mapped[str] = mapped_column(String(200))



