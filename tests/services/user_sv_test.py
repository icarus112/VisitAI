from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import User
from app.service.user import UserService
from app.shemas.record import UserCreate
from tests.factories import ModelFactory


@pytest.fixture
def user_sv():
    return UserService(AsyncMock())

@pytest.mark.asyncio
async def test_create_user_error(user_sv: UserService):
    user_sv.us_rp.create_user = Mock()
    user_sv.us_rp.create_user.side_effect = Exception("user create error")
    with pytest.raises(Exception, match="user create error"):
        await user_sv.create_user("name", 123, "43")

@pytest.mark.asyncio(
    loop_scope = "session"
)
async def test_create_user_success(
        session_test: AsyncSession,
        user_sv: UserService):
    factory = ModelFactory(session_test)
    user = await factory.create_user()
    user_sv.us_rp.create_user = AsyncMock()
    user_sv.us_rp.create_user.return_value = user

    create_user = UserCreate(
            tg_id=user.tg_id,
            name=user.name,
            phone=user.phone
        )

    await user_sv.create_user(user.name, user.tg_id, user.phone)

    user_sv.us_rp.create_user.assert_awaited_once_with(
        create_user
    )


