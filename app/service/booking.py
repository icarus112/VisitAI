from datetime import datetime, time, date
import logging

from app.shemas.record import BookingCreate, BookingRequestResult
from app.database.models import Booking
from app.core.enum import BookStatus, PaymentMethod

logger = logging.getLogger(__name__)

class BookingService:
    def __init__(self, bk_rp, us_rp, ct_rp, ad_rp):
        self.bk_rp = bk_rp
        self.us_rp = us_rp
        self.ct_rp = ct_rp
        self.ad_rp = ad_rp

    def today(self) -> date:
        return date.today()

    async def create_booking(self,
                             tg_id: int,
                             ct_id: int,
                             date_str: str,
                             time_str: str,
                             comment: str) -> BookingRequestResult:
        user = await self.us_rp.get_by_tg_id(tg_id)
        ct = await self.ct_rp.get_ct_by_id(ct_id)
        active_field = datetime.now()

        if not user:
            logger.warning(f"user is not found for creating booking, user tg_id={tg_id}")
            raise ValueError("Пользователь не найден в sv")

        if not ct:
            logger.warning(f"ct is not found for creating booking, ct id={ct_id}")
            raise ValueError("Услуга не найдена в sv")

        if isinstance(date_str, date):#если date_str принадлежит к datetime.date
            booking_date = date_str
        elif isinstance(date_str, str):#если date_str принадлежит к str
            booking_date = self.parse_date(date_str)
        else:
            logger.warning("wrong date format for creating booking, date_str= ", date_str)
            raise ValueError("Неверный тип даты в sv")
        parsed_time = self.parse_time(time_str)

        scheduled_at = datetime.combine(booking_date, parsed_time)

        if scheduled_at <= active_field:
            logger.warning("booking is rejected cause of wrong date/time:"
                           f"date:{date_str}, time:{parsed_time}")
            raise ValueError("Дата и время не должно быть в прошлом времени")

        booking = BookingCreate(
            user_id=user.id,
            catalog_id=ct_id,
            scheduled_at=scheduled_at,
            price=ct.price,
            status=BookStatus.PENDING,
            payment_method=PaymentMethod.PENDING,
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

    async def page_text(self,
                        bk: Booking
                        ):
        try:
            ct = await self.ct_rp.get_ct_by_id(bk.catalog_id)
            tran_status = self.translate_booking_status(bk.status)
        except Exception:
            logger.warning("error for bk_page_text")
            raise

        return (f"\nУслуга: {ct.name}"
        f"\nДата: {bk.scheduled_at.date().strftime('%Y.%m.%d')}"
        f"\nВремя: {bk.scheduled_at.time()}"
        f"\nСтатус: {tran_status}")

    async def page_data(self, page: int, user_id: int):

        total = await self.bk_rp.count_my_bk(user_id)

        if total == 0:
            return [], 0

        if page < 0:
            page = 0

        if page >= total:
            page = total - 1

        bk = await self.bk_rp.get_bk_page(page, user_id)

        return bk, page, total

    def parse_date(self, date_str: str) -> date:
        wd = date_str.split(".")
        wd = [el for el in wd if el != ""]

        month = date.today().month
        year = date.today().year

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
            return datetime.strptime(new_wd, "%Y.%m.%d").date()
        except ValueError:
            logging.warning(f"can't parse date for creating booking , date_str= {date_str}")
            raise ValueError("Ошибка при переводе даты в sv")

    def parse_time(self, time_str: str) -> time:
        time_str = time_str.strip().replace(" ", ":")

        try:
            return time.fromisoformat(time_str)
        except ValueError:
            logger.warning(f"wrong time format for creating booking, time_str= {time_str}")
            raise

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

    async def get_full_bk(self, bk_id: int) -> Booking | None:
        try:
            full_bk = await self.bk_rp.get_full_bk(bk_id)

        except Exception:
            logger.exception(
                f"Failed to get booking "
                f"booking_id={bk_id}"
            )
            raise

        if full_bk is None:
            logger.warning(
                f"booking not found "
                f"booking_id={bk_id}"
            )

        return full_bk

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

    async def remove_bk(self, bk_id: int) -> None:
        bk = await self.bk_rp.get_booking(bk_id)

        if bk is None:
            raise ValueError(f"Booking {bk_id} not found")

        return await self.bk_rp.remove_bk(bk_id)

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
                tran_status = self.translate_booking_status(bk.status)
                lines.append("\n\n______________________________")
                lines.append(f"\nУслуга: {ct.name}")
                lines.append(f"Дата: {bk.scheduled_at.date().strftime('%Y.%m.%d')}")
                lines.append(f"Время: {bk.scheduled_at.time().strftime('%H:%M')}")
                lines.append(f"Статус: {tran_status}")

            text += "\n".join(lines)
            return text

    def translate_booking_status(self, status: BookStatus) -> str:
        translations = {
            BookStatus.PENDING: "Ожидает подтверждения",
            BookStatus.CONFIRMED: "Запись подтверждена",
            BookStatus.CANCELLED: "Запись отменена",
            BookStatus.COMPLETED: "Услуга оказана",
            BookStatus.NO_SHOW: "Клиент не пришёл",
        }

        try:
            return translations[status]
        except KeyError:
            logger.warning(
                "translate_booking_status failed for status: %s",
                status,
            )
            raise ValueError(
                f"Неизвестный статус бронирования: {status}"
            )

