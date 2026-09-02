from unittest.mock import AsyncMock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.conf import settings
from app.core.enum import AdminRole
from app.database import Admin
from app.repository.admin import AdminRepos
from app.service.admin import AdminService
from tests.factories import ModelFactory


@pytest.mark.asyncio
async def test_get_ad_by_tg_id_success():
    repo = AsyncMock(spec=AdminRepos)

    admin = Admin(
        name="admin",
        tg_id=123,
        role=AdminRole.ADMIN
    )
    repo.get_ad_by_tg_id.return_value = admin

    service = AdminService(ad_rp = repo)

    result = await service.get_ad_by_tg_id(tg_id=123)

    assert result is admin
    repo.get_ad_by_tg_id.assert_awaited_once_with(123)

@pytest.mark.asyncio
async def test_get_ad_by_tg_id_returns_none():
    repo = AsyncMock(spec=AdminRepos)
    repo.get_ad_by_tg_id.side_effect = RuntimeError("database error")

    service = AdminService(ad_rp = repo)
    result = await service.get_ad_by_tg_id(tg_id=123)

    assert result is None
    repo.get_ad_by_tg_id.assert_awaited_once_with(123)

@pytest.mark.asyncio
async def test_change_role_false_dev_mode(monkeypatch):
    repo = AsyncMock(spec=AdminRepos)
    monkeypatch.setattr(settings, "dev_mode", False)

    service = AdminService(ad_rp = repo)

    with pytest.raises(PermissionError):
        await service.change_role(tg_id=123, new_role="super_admin")
    repo.change_role.assert_not_awaited()

@pytest.mark.asyncio
async def test_change_role_value_error(monkeypatch):
    repo = AsyncMock(spec=AdminRepos)
    monkeypatch.setattr(settings, "dev_mode", True)
    service = AdminService(ad_rp = repo)

    with pytest.raises(ValueError):
        await service.change_role(tg_id=123, new_role="batman")
    repo.change_role.assert_not_awaited()

@pytest.mark.asyncio
async def test_change_role_success(monkeypatch):
    repo = AsyncMock(spec=AdminRepos)
    monkeypatch.setattr(settings, "dev_mode", True)
    service = AdminService(ad_rp = repo)

    result = await service.change_role(tg_id=123, new_role="super_admin")

    assert result is AdminRole.SUPER_ADMIN
    repo.change_role.assert_awaited_once_with(tg_id=123, new_role=AdminRole.SUPER_ADMIN)

@pytest.mark.asyncio
async def test_get_info_empty():
    repo = AsyncMock(spec=AdminRepos)
    repo.get_all_admin.return_value = []
    service = AdminService(ad_rp = repo)

    result = await service.get_info()

    assert result == "Список пуст, сотрудников нету"

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_get_info_success(session_test: AsyncSession):
    repo = AsyncMock(spec=AdminRepos)
    factory = ModelFactory(session_test)
    admin = await factory.create_admin()

    repo.get_all_admin.return_value = [admin]
    service = AdminService(ad_rp = repo)

    result = await service.get_info()

    assert admin.name in result
    assert str(admin.tg_id) in result
    assert admin.role in result

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_remove_admin_none_admin(session_test: AsyncSession):
    repo = AsyncMock(spec=AdminRepos)
    factory = ModelFactory(session_test)
    admin_1 = await factory.create_admin()

    repo.remove_admin_by_id.return_value = None

    service = AdminService(ad_rp = repo)

    result = await service.remove_admin_by_id(admin_1.id)

    assert result is None
    repo.remove_admin_by_id.assert_awaited_once_with(admin_1.id)

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_remove_admin_success(session_test: AsyncSession):
    repo = AsyncMock(spec=AdminRepos)
    factory = ModelFactory(session_test)
    admin_1 = await factory.create_admin()

    repo.get_ad_by_id.return_value = admin_1
    repo.remove_admin_by_id.return_value = admin_1
    service = AdminService(ad_rp = repo)

    result = await service.remove_admin_by_id(admin_1.id)

    assert result.id == admin_1.id
    repo.remove_admin_by_id.assert_awaited_once_with(admin_1.id)



