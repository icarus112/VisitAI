from decimal import Decimal

from freezegun import freeze_time
from typing import Self
from unittest.mock import AsyncMock
from datetime import datetime
from datetime import date
from datetime import time
import pytest

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