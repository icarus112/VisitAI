import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker

from app.core.conf import settings

@pytest_asyncio.fixture(
    scope="session",
    loop_scope="session",
)
async def engine_test():
    engine = create_async_engine(settings.database_test_url)

    yield engine

    await engine.dispose()

@pytest_asyncio.fixture(
    scope="function",#  livetime of fixture, always creating new fixture for every test
    loop_scope="session",# livetime of event_loop
)
async def session_test(engine_test: AsyncEngine) -> AsyncSession:
    async with engine_test.connect() as conn:
        transaction = await conn.begin()

        SessionLocal = async_sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        async with SessionLocal() as session:
            yield session

        if transaction.is_active:
            await transaction.rollback()
