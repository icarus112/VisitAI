import asyncio
import logging
from sqlalchemy import text

from app.scripts.seed_db import fill_ct, fill_faq, fill_bk, has_any
from app.core.conf import settings
from app.database.async_engine import async_engine
from app.database.models import Base, Catalog, Booking, Faq

logger = logging.getLogger(__name__)

async def init_db():
    async with async_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.run_sync(Base.metadata.create_all)

    if settings.dev_mode:
        if not await has_any(Catalog):
            await fill_ct()
            logger.info("Catalog seeds filled")
        else:
            logger.info("Catalog seeds skipped")

        if not await has_any(Faq):
            await fill_faq()
            logger.info("Faq seeds filled")
        else:
            logger.info("Faq seeds skipped")

        if not await has_any(Booking):
            await fill_bk()
            logger.info("Booking seeds filled")
        else:
            logger.info("Booking seeds skipped")

if __name__ == "__main__":
    asyncio.run(init_db())
    # print(async_engine.url)