import asyncio
import logging
from sqlalchemy import text

from app.database.async_engine import async_engine
from app.database.models import Base

logger = logging.getLogger(__name__)

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
    # print(async_engine.url)