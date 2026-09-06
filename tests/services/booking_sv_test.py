from decimal import Decimal

from freezegun import freeze_time
from typing import Self
from unittest.mock import AsyncMock, Mock
from datetime import datetime
from datetime import date
from datetime import time
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enum import BookStatus, PaymentMethod
from app.repository.admin import AdminRepos
from app.repository.booking import BookingRepos
from app.repository.catalog import CatalogRepos
from app.repository.user import UserRepos
from app.service.booking import BookingService
from app.shemas.record import BookingCreate, BookingRead, UserRead, CatalogRead
from tests.factories import ModelFactory


class FakeDatetime(datetime):
    @classmethod
    def today(cls) -> Self:
        return cls(1970, 1, 1, 16, 10, 50)

@pytest.fixture
def bk_service(monkeypatch):
    bk_rp = AsyncMock(spec=BookingRepos)
    us_rp = AsyncMock(spec=UserRepos)
    ct_rp = AsyncMock(spec=CatalogRepos)
    ad_rp = AsyncMock(spec=AdminRepos)

    us_rp.get_by_tg_id.return_value = None
    ct_rp.get_ct_by_id.return_value = None

    return BookingService(bk_rp, us_rp, ct_rp, ad_rp)

@pytest.fixture
def bk_service_with_fake_date(monkeypatch):
    bk_rp = AsyncMock(spec=BookingRepos)
    us_rp = AsyncMock(spec=UserRepos)
    ct_rp = AsyncMock(spec=CatalogRepos)
    ad_rp = AsyncMock(spec=AdminRepos)

    us_rp.get_by_tg_id.return_value = None
    ct_rp.get_ct_by_id.return_value = None

    monkeypatch.setattr("app.service.booking.date", FakeDatetime)

    return BookingService(bk_rp, us_rp, ct_rp, ad_rp)

@pytest.mark.parametrize("bad_date", [
    "2.4.2021.9", "2.14", "q.aq.ewwq"
])
def test_parse_date_wrong_str(bk_service_with_fake_date, bad_date):
    with pytest.raises(ValueError):
        bk_service_with_fake_date.parse_date(bad_date)

@pytest.mark.parametrize("input_date, expected", [
    ("15", date(1970, 1, 15)),
    ("12.03", date(1970, 3, 12)),
    ("12.03.1971", date(1971, 3, 12)),
])
def test_parse_date_success(
        bk_service_with_fake_date,
        input_date,
        expected):

    result = bk_service_with_fake_date.parse_date(input_date)
    assert result == expected

@pytest.mark.parametrize("bad_time", [
    "a2:10", "12:60", "12;10", "12:1"
])
def test_parse_time_wrong_str(bk_service, bad_time):
    with pytest.raises(ValueError):
        bk_service.parse_time(bad_time)

@pytest.mark.parametrize("input_time, expected" , [
    ("12:45", time(12, 45)),
    ("12 45", time(12, 45))
])
def test_parse_time_success(bk_service, input_time, expected):
    result = bk_service.parse_time(input_time)
    assert result == expected

@pytest.mark.asyncio
async def test_create_booking_none_user(bk_service : BookingService):
    bk_rp = AsyncMock(spec=BookingRepos)
    bk_service.us_rp.get_by_tg_id.return_value = None

    with pytest.raises(ValueError):
        await bk_service.create_booking(
            tg_id=123,
            ct_id=123,
            date_str="date",
            time_str="time",
            comment="comment"
        )
    bk_rp.create_booking.assert_not_awaited()

@pytest.mark.asyncio
async def test_create_booking_none_catalog(bk_service : BookingService):
    bk_rp = AsyncMock(spec=BookingRepos)
    user = AsyncMock()
    bk_service.us_rp.get_by_tg_id.return_value = user

    with pytest.raises(ValueError):
        await bk_service.create_booking(
            tg_id=123,
            ct_id=123,
            date_str="date",
            time_str="time",
            comment="comment"
        )
    bk_rp.create_booking.assert_not_awaited()

@pytest.mark.asyncio
@pytest.mark.parametrize("past_date, past_time", [
    ("1.01.1969", "18 50"),
    ("1.01.1970", "11:10")
])
async def test_create_booking_past_scheduled_at(
        past_date,
        past_time,
        bk_service_with_fake_date : BookingService):
    user = AsyncMock()
    catalog = AsyncMock()

    bk_service_with_fake_date.us_rp.get_by_tg_id.return_value = user
    bk_service_with_fake_date.ct_rp.get_ct_by_id.return_value = catalog

    with pytest.raises(ValueError):
        await bk_service_with_fake_date.create_booking(
            tg_id=123,
            ct_id=123,
            date_str=past_date,
            time_str=past_time,
            comment="comment"
        )


@freeze_time("1970-01-01")#что бы active field был в этом времени
@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_create_booking_success(
        bk_service_with_fake_date,
        session_test):
    factory = ModelFactory(session_test)
    user = await factory.create_user()
    catalog = await factory.create_catalog()
    new_booking = await factory.create_booking(
        user=user,
        catalog=catalog,
        scheduled_at=datetime(1970, 1, 15, 20, 0),
        price=Decimal(catalog.price),
        status=BookStatus.PENDING,
        payment_method=PaymentMethod.PENDING,
    )

    bk_service_with_fake_date.us_rp.get_by_tg_id.return_value = user
    bk_service_with_fake_date.ct_rp.get_ct_by_id.return_value = catalog
    bk_service_with_fake_date.bk_rp.create_booking.return_value = new_booking

    result = await bk_service_with_fake_date.create_booking(
        tg_id=user.tg_id,
        ct_id=catalog.id,
        date_str="15",
        time_str="20 00",
        comment="comment"
    )

    booking_read = BookingRead(
        id=new_booking.id,
        user_id=user.id,
        catalog_id = catalog.id,
        scheduled_at = datetime(1970, 1, 15, 20, 0),
        status = new_booking.status,
        comment = result.comment
    )

    user_read = UserRead(
        id=user.id,
        tg_id=user.tg_id,
        name=user.name,
        phone=user.phone,
    )

    catalog_read = CatalogRead(
        id=catalog.id,
        name=catalog.name,
        price=catalog.price,
        duration=catalog.duration,
    )

    assert result.booking == booking_read
    assert result.user == user_read
    assert result.ct == catalog_read
    assert result.comment == "comment"

    bk_service_with_fake_date.bk_rp.create_booking.assert_awaited_once_with(
        BookingCreate(
            user_id=user.id,
            catalog_id=catalog.id,
            scheduled_at=datetime(1970, 1, 15, 20, 0),
            price=catalog.price,
            status=BookStatus.PENDING,
            payment_method=PaymentMethod.PENDING,
            comment="comment"
        )
    )

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_page_text_success(session_test: AsyncSession,
                                 bk_service: BookingService):
    factory = ModelFactory(session_test)
    booking = await factory.create_booking()
    ct = await factory.create_catalog(name="test_name")
    trans_status = "my_status"
    bk_service.translate_booking_status = Mock()

    bk_service.ct_rp.get_ct_by_id.return_value = ct
    bk_service.translate_booking_status.return_value = trans_status

    text = await bk_service.page_text(booking)

    assert ct.name in text
    assert booking.scheduled_at.date().strftime('%Y.%m.%d') in text
    assert str(booking.scheduled_at.time()) in text
    assert trans_status in text
    bk_service.ct_rp.get_ct_by_id.assert_awaited_once_with(booking.catalog_id)
    bk_service.translate_booking_status.assert_called_once_with(BookStatus.CONFIRMED)

@pytest.mark.asyncio()
async def test_page_text_wrong_ct(bk_service: BookingService):
    booking = Mock()
    bk_service.ct_rp.get_ct_by_id.side_effect = Exception("test error")
    bk_service.translate_booking_status = Mock()

    with (pytest.raises(Exception)):
        await bk_service.page_text(booking)

    bk_service.translate_booking_status.assert_not_called()

@pytest.mark.asyncio()
async def test_page_text_wrong_trans_status(bk_service: BookingService):
    booking = Mock()
    ct = Mock()
    bk_service.ct_rp.get_ct_by_id.return_value = ct
    bk_service.translate_booking_status = Mock()
    bk_service.translate_booking_status.side_effect = Exception("test error")

    with pytest.raises(Exception):
        await bk_service.page_text(booking)

@pytest.mark.asyncio()
async def test_page_data_zero_total(bk_service: BookingService):
    bk_service.bk_rp.count_my_bk.return_value = 0

    result = await bk_service.page_data(page=1, user_id=1)

    assert result == ([], 0)
    bk_service.bk_rp.get_bk_page.assert_not_awaited()


@pytest.mark.asyncio()
async def test_page_data_page_under_zero(bk_service: BookingService):
    bk = Mock()
    total = 10
    bk_service.bk_rp.count_my_bk.return_value = total
    bk_service.bk_rp.get_bk_page.return_value = bk

    result = await bk_service.page_data(page=1, user_id=9)

    assert result == (bk, 1, 10)
    bk_service.bk_rp.get_bk_page.assert_awaited_once_with(1, 9)

@pytest.mark.asyncio()
async def test_page_data_total_under_page(bk_service: BookingService):
    bk = Mock()
    total = 10
    bk_service.bk_rp.count_my_bk.return_value = total
    bk_service.bk_rp.get_bk_page.return_value = bk

    result = await bk_service.page_data(page=15, user_id=1)

    assert result == (bk, 9, 10)
    bk_service.bk_rp.get_bk_page.assert_awaited_once_with(9, 1)

@pytest.mark.asyncio()
async def test_get_booking_exception_error(bk_service: BookingService):
    bk_service.bk_rp.get_booking.side_effect = Exception("test error")

    with pytest.raises(Exception):
        await bk_service.get_booking(2)

@pytest.mark.asyncio()
async def test_get_booking_none_booking(bk_service: BookingService):
    bk_service.bk_rp.get_booking.return_value = None

    booking = await bk_service.bk_rp.get_booking(2)

    assert booking is None

@pytest.mark.asyncio()
async def test_get_booking_success(
        bk_service: BookingService):
    booking = Mock()
    bk_service.bk_rp.get_booking.return_value = booking

    result = await bk_service.bk_rp.get_booking(2)

    assert result == booking

@pytest.mark.asyncio()
async def test_cancel_pay_zero_rowcount(bk_service: BookingService):
    bk_service.bk_rp.cancel_pay.return_value = 0

    with pytest.raises(RuntimeError):
        await bk_service.cancel_pay(2)
    bk_service.bk_rp.cancel_pay.assert_awaited_once_with(2)

@pytest.mark.asyncio()
async def test_cancel_pay_success(bk_service: BookingService):
    bk_service.bk_rp.cancel_pay.return_value = 1

    result = await bk_service.cancel_pay(2)

    assert result is True
    bk_service.bk_rp.cancel_pay.assert_awaited_once_with(2)


@pytest.mark.asyncio()
async def test_remove_bk_error(bk_service: BookingService):
    bk_service.bk_rp.remove_bk.return_value = 0

    with pytest.raises(Exception):
        await bk_service.remove_bk(2)
    bk_service.bk_rp.remove_bk.assert_awaited_once_with(2)


@pytest.mark.asyncio()
async def test_remove_success(bk_service: BookingService):
    bk_service.bk_rp.remove_bk.return_value = 1

    result = await bk_service.remove_bk(2)

    assert result == 1
    bk_service.bk_rp.remove_bk.assert_awaited_once_with(2)

@pytest.mark.asyncio()
async def test_my_bk_info_empty_my_bks(bk_service: BookingService):
    bk_service.bk_rp.get_my_bookings.return_value = []

    result = await bk_service.my_bk_info(2)

    assert result == "Список пуст, услуг на данный момент не обнаружена"
    bk_service.bk_rp.get_my_bookings.assert_awaited_once_with(2)

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_my_bk_info_success(
        session_test: AsyncSession,
        bk_service: BookingService):
    factory = ModelFactory(session_test)
    bk = await factory.create_booking()
    ct = await factory.create_catalog(name="test_name")
    bk_service.translate_booking_status = Mock()

    bk_service.translate_booking_status.return_value = "bk_test_status"
    bk_service.bk_rp.get_my_bookings.return_value = [bk]
    bk_service.ct_rp.get_ct_by_id.return_value = ct

    text = await bk_service.my_bk_info(1)

    assert "Ваши созданные заявки:" in text
    assert ct.name in text
    assert bk.scheduled_at.date().strftime("%Y.%m.%d") in text
    assert bk.scheduled_at.time().strftime("%H:%M") in text
    assert "bk_test_status" in text

    bk_service.bk_rp.auto_complete_old.assert_awaited_once_with(1)
    bk_service.bk_rp.get_my_bookings.assert_awaited_once_with(1)
    bk_service.ct_rp.get_ct_by_id.assert_awaited_once_with(bk.catalog_id)

    bk_service.translate_booking_status.assert_called_once_with(bk.status)

@pytest.mark.parametrize(
    "status, expected",
    [
        (BookStatus.PENDING, "Ожидает подтверждения"),
        (BookStatus.CONFIRMED, "Запись подтверждена"),
        (BookStatus.CANCELLED, "Запись отменена"),
        (BookStatus.COMPLETED, "Услуга оказана"),
        (BookStatus.NO_SHOW, "Клиент не пришёл"),
    ],
)
def test_translate_booking_status_success(
        bk_service: BookingService,
        status: BookStatus,
        expected: str,
):
    result = bk_service.translate_booking_status(status)

    assert result == expected


def test_translate_booking_status_unknown_status(
        bk_service: BookingService,
):
    wrong_status = "WRONG_STATUS"

    with pytest.raises(
        KeyError,
        match="Неизвестный статус бронирования",
    ):
        bk_service.translate_booking_status(wrong_status)