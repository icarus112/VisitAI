import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import User

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_database(
        session_test: AsyncSession
):
    user = User(
        tg_id = 67,
        name = "gay",
        phone = "234324"
    )

    session_test.add(user)
    await session_test.flush()
    stmt = (select(User)
            .where(User.tg_id==67))
    res = await session_test.execute(stmt)
    check = res.scalar_one_or_none()

    assert check is not None
    assert check.name == "gay"
    assert check.id == user.id

