import asyncio

from sqlalchemy import text

from database.async_engine import async_engine
from database.models import Base

async def init_db():
    async with async_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
    # print(async_engine.url)