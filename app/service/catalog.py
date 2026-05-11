from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import List

from app.shemas.catalog import CatalogCreate, CatalogResponse

from database.models import Catalog


class CatalogService:
    def __init__(self, ct_rp):
        self.ct_rp = ct_rp

    async def str_to_decimal(self, text: str) -> Decimal:
        t = text.strip().replace(",", ".")

        try:
            value = Decimal(t)
        except InvalidOperation:
            raise ValueError("нужно число например 1.5")

        if value < 0:
            raise ValueError("Число должны быть положительными или 0")

        return value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


    async def create_ct(self, name, price, duration) -> CatalogResponse:
        if not name:
            raise ValueError("Название не может быть пустым")

        price = await self.str_to_decimal(price)

        try:
            duration = int(duration)
        except Exception:
            raise ValueError("Длительность должна быть числом, например 30")

        if duration <= 0:
            raise ValueError("Длительность должна быть больше 0")

        ct = CatalogCreate(
            name=name,
            price=price,
            duration=duration,
        )
        return await self.ct_rp.create_ct(ct)

    async def get_all(self) -> List[Catalog]:
        catalogs = await self.ct_rp.get_all()
        if not catalogs:
            raise ValueError("ничего не найдено")

        return catalogs

    async def get_ct_by_id(self, ct_id: int) -> Catalog:
        selected = await self.ct_rp.get_ct_by_id(ct_id)

        return selected

    async def find_by_name(self, query: str) -> Catalog:
        return await self.ct_rp.find_by_name(query)

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