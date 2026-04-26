from decimal import Decimal

from app.repository.catalog import CatalogRepos
from app.shemas.catalog import CatalogCreate

import asyncio
from database.async_engine import async_session

class CatalogService:
    def __init__(self, ct_rp):
        self.ct_rp = ct_rp

    async def create_ct(self, ct: CatalogCreate):
        return await self.ct_rp.create_ct(ct)

# async def prog():
#     async with async_session() as session:
#         ct_rp = CatalogRepos(session)
#         sv = CatalogService(ct_rp)
#
#         ct = CatalogCreate(
#             name="herna",
#             price=Decimal("32.00"),
#             duration=30
#         )
#
#         result = await sv.create_ct(ct)
#
#         await session.commit()
#
#         print(result)
#
# if __name__ == "__main__":
#     asyncio.run(prog())

