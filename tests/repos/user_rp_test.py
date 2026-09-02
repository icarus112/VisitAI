import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.user import UserRepos
from app.shemas.record import UserCreate


@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_create_user(session_test: AsyncSession):
    us_rp = UserRepos(session_test)

    user = UserCreate(
        tg_id=123,
        name="user_1",
        phone="+99362560816"
    )

    result = await us_rp.create_user(user)
    await session_test.flush()

    assert result.id is not None
    assert result.name == user.name
    assert result.phone == user.phone


