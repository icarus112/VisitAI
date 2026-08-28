from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.core.enum import BookStatus, PaymentMethod
from app.repository.booking import BookingRepos
from app.shemas.record import BookingCreate
from tests.factories import ModelFactory

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_creating_bookings(
        session_test: AsyncSession
):
    bk_rp = BookingRepos(session_test)
    factory = ModelFactory(session_test)
    user = await factory.create_user()
    catalog =await factory.create_catalog()

    booking_base = BookingCreate(
        user_id = user.id,
        catalog_id=catalog.id,
        scheduled_at=factory.base_time,
        price=Decimal('300'),
        status=BookStatus.CONFIRMED,
        payment_method=PaymentMethod.ONLINE,
    )
    booking = await bk_rp.create_booking(booking_base)

    assert booking is not None
    assert booking.id is not None
    assert booking.user_id == user.id
    assert booking.catalog_id == catalog.id
    assert booking.status == BookStatus.CONFIRMED
    assert booking.payment_method == PaymentMethod.ONLINE

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_get_my_bookings(session_test: AsyncSession):
    bk_rp = BookingRepos(session_test)
    factory = ModelFactory(session_test)

    user_1 = await factory.create_user()
    user_2 = await factory.create_user()
    booking_1 = await factory.create_booking(
        user=user_1,
        scheduled_at=(factory.base_time + timedelta(hours=3)),
        status=BookStatus.CONFIRMED)
    booking_2 = await factory.create_booking(
        user=user_1,
        status=BookStatus.COMPLETED)
    booking_3 = await factory.create_booking(
        user=user_1,
        status=BookStatus.CONFIRMED)
    another_booking = await factory.create_booking(
        user=user_2,
        status=BookStatus.CONFIRMED)

    my_bookings = await bk_rp.get_my_bookings(us_id=user_1.id)

    assert len(my_bookings) == 2
    assert [bk.id for bk in my_bookings] == [booking_3.id, booking_1.id]


@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_count_bk(session_test: AsyncSession):
    bk_rp = BookingRepos(session_test)
    factory = ModelFactory(session_test)

    user_1 = await factory.create_user()
    user_2 = await factory.create_user()
    booking_1 = await factory.create_booking(
        user=user_1,
        scheduled_at=(factory.base_time + timedelta(hours=3)),
        status=BookStatus.CONFIRMED)
    booking_2 = await factory.create_booking(
        user=user_1,
        status=BookStatus.COMPLETED)
    booking_3 = await factory.create_booking(
        user=user_1,
        status=BookStatus.PENDING)
    another_booking = await factory.create_booking(
        user=user_2,
        status=BookStatus.CONFIRMED)

    count = await bk_rp.count_my_bk(user_id=user_1.id)

    await session_test.refresh(booking_1)
    await session_test.refresh(booking_2)
    await session_test.refresh(booking_3)
    await session_test.refresh(another_booking)

    assert (count == 2)

@pytest.mark.asyncio(
    loop_scope="session")
async def test_get_bk_page(session_test: AsyncSession):
    bk_rp = BookingRepos(session_test)
    factory = ModelFactory(session_test)

    user_1 = await factory.create_user()
    user_2 = await factory.create_user()
    booking_1 = await factory.create_booking(
        user=user_1,
        scheduled_at=(factory.base_time + timedelta(hours=3)),
        status=BookStatus.CONFIRMED)
    booking_2 = await factory.create_booking(
        user=user_1,
        status=BookStatus.COMPLETED)
    booking_3 = await factory.create_booking(
        user=user_1,
        status=BookStatus.PENDING)
    another_booking_4 = await factory.create_booking(
        user=user_2,
        status=BookStatus.CANCELLED)
    another_booking_5 = await factory.create_booking(
        user=user_2,
        status=BookStatus.CONFIRMED)


    bk_1 = await bk_rp.get_bk_page(page=1, user_id=user_1.id)
    another_bk_1 = await bk_rp.get_bk_page(page=0, user_id=user_2.id)
    none_booking = await bk_rp.get_bk_page(page=89, user_id=user_2.id)

    await session_test.refresh(booking_1)
    await session_test.refresh(booking_2)
    await session_test.refresh(booking_3)
    await session_test.refresh(another_booking_4)
    await session_test.refresh(another_booking_5)

    assert bk_1.id == booking_1.id
    assert another_bk_1.id == another_booking_5.id
    assert none_booking is None

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_auto_complete_old(session_test: AsyncSession):
    bk_rp = BookingRepos(session_test)
    factory = ModelFactory(session_test)

    user_1 = await factory.create_user()
    user_2 = await factory.create_user()

    now = datetime.now()

    # Должна стать COMPLETED:
    # нужный пользователь + активный статус + старше 3 часов
    booking_1 = await factory.create_booking(
        user=user_1,
        scheduled_at=now - timedelta(hours=4),
        status=BookStatus.CONFIRMED,
    )
    # Не должна измениться:
    # нужный пользователь, активная, но ещё не прошло 3 часа
    booking_2 = await factory.create_booking(
        user=user_1,
        scheduled_at=now - timedelta(hours=1),
        status=BookStatus.PENDING,
    )
    # Не должна измениться:
    # уже COMPLETED
    booking_3 = await factory.create_booking(
        user=user_1,
        scheduled_at=now - timedelta(hours=5),
        status=BookStatus.COMPLETED,
    )
    # Не должна измениться:
    # старая и активная, но другой пользователь
    another_booking_4 = await factory.create_booking(
        user=user_2,
        scheduled_at=now - timedelta(hours=5),
        status=BookStatus.PENDING,
    )
    # Не должна измениться:
    # другой пользователь + неактивный статус
    another_booking_5 = await factory.create_booking(
        user=user_2,
        scheduled_at=now - timedelta(hours=5),
        status=BookStatus.CANCELLED,
    )

    updated_count = await bk_rp.auto_complete_old(us_id=user_1.id)

    await session_test.refresh(booking_1)
    await session_test.refresh(booking_2)
    await session_test.refresh(booking_3)
    await session_test.refresh(another_booking_4)
    await session_test.refresh(another_booking_5)

    assert updated_count == 1

    assert booking_1.status == BookStatus.COMPLETED
    assert booking_2.status == BookStatus.PENDING
    assert booking_3.status == BookStatus.COMPLETED

    assert another_booking_4.status == BookStatus.PENDING
    assert another_booking_5.status == BookStatus.CANCELLED

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_cancel_pay(session_test: AsyncSession):
    bk_rp = BookingRepos(session_test)
    factory = ModelFactory(session_test)

    booking = await factory.create_booking(
        status=BookStatus.PENDING
    )

    updated_count = await bk_rp.cancel_pay(
        booking_id=booking.id
    )

    await session_test.refresh(booking)

    assert updated_count == 1
    assert booking.status == BookStatus.CONFIRMED

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_remove_bk(session_test: AsyncSession):
    bk_rp = BookingRepos(session_test)
    factory = ModelFactory(session_test)

    booking = await factory.create_booking(
        status=BookStatus.CONFIRMED
    )

    updated_count = await bk_rp.remove_bk(
        bk_id=booking.id
    )

    await session_test.refresh(booking)

    assert updated_count == 1
    assert booking.status == BookStatus.REMOVED