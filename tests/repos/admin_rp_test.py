import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enum import AdminRole
from app.repository.admin import AdminRepos
from tests.factories import ModelFactory


@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_is_admin(
        session_test: AsyncSession):
    ad_rp = AdminRepos(session_test)
    factory = ModelFactory(session_test)

    admin = await factory.create_admin()

    is_admin_1 = await ad_rp.is_admin(admin.tg_id)
    false_admin = await ad_rp.is_admin(6767)

    assert is_admin_1 is True
    assert false_admin is False

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_create_admin(
        session_test: AsyncSession):
    ad_rp = AdminRepos(session_test)

    res = await ad_rp.create_admin(tg_id=1984,
                                   name="master")

    assert res.tg_id == 1984
    assert res.name == "master"
    assert res.role == AdminRole.ADMIN

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_get_all_admin(session_test: AsyncSession):
    factory = ModelFactory(session_test)
    ad_rp = AdminRepos(session_test)

    old_arr = await ad_rp.get_all_admin()


    admin_1 = await factory.create_admin(name="admin1")
    admin_2 = await factory.create_admin(name="admin2")

    arr = await ad_rp.get_all_admin()
    assert len(arr) == len(old_arr) + 2
    assert [arr[i].id for i in  range(len(old_arr), len(old_arr)+2)] == [admin_1.id, admin_2.id]


@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_change_role(session_test: AsyncSession):
    factory = ModelFactory(session_test)
    ad_rp = AdminRepos(session_test)

    admin_1 = await factory.create_admin(name="admin1",
                                         role=AdminRole.ADMIN)
    admin_2 = await factory.create_admin(name="admin2",
                                         role=AdminRole.ADMIN)

    await ad_rp.change_role(admin_1.tg_id, AdminRole.SUPER_ADMIN)

    await session_test.flush()
    await session_test.refresh(admin_1)
    await session_test.refresh(admin_2)

    assert admin_1.role == AdminRole.SUPER_ADMIN
    assert admin_2.role != AdminRole.SUPER_ADMIN

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_remove_admin(session_test: AsyncSession):

    factory = ModelFactory(session_test)
    ad_rp = AdminRepos(session_test)

    admin_1 = await factory.create_admin(name="admin1")
    await session_test.flush()

    is_removed = await ad_rp.remove_admin_by_id(admin_1.id)

    await session_test.flush()

    none_admin = await ad_rp.get_ad_by_id(admin_1.id)

    assert is_removed is True
    assert none_admin is None

