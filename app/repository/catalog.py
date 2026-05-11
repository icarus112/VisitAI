from typing import List
from unittest import result

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shemas import catalog
from app.shemas.catalog import CatalogCreate, CatalogResponse
from database.models import Catalog


class CatalogRepos:
    def __init__(self, session):
        self.session = session

    async def create_ct(self, add_catalog: CatalogCreate) -> CatalogResponse:
        catalog = Catalog(**add_catalog.model_dump())

        self.session.add(catalog)
        await self.session.flush()
        await self.session.refresh(catalog)

        result = CatalogResponse(
            id=catalog.id,
            name=catalog.name,
            price=catalog.price,
            duration=catalog.duration
        )

        return result

    async def get_all(self) -> List[Catalog]:
        stmt = (select(Catalog).order_by(Catalog.id))

        results = await self.session.execute(stmt)
        catalogs = results.scalars().all()
        return catalogs

    async def get_ct_by_id(self, id: int) -> Catalog:
        stmt = (select(Catalog)
                .where(Catalog.id == id))

        result = await self.session.execute(stmt)
        catalog = result.scalar_one_or_none()
        return catalog

    async def find_by_name(self, query: str) -> Catalog:
        stmt = (select(Catalog)
                .where(Catalog.name.ilike( f"%{query}%"))
                )
        result = await self.session.execute(stmt)
        catalog = result.scalar_one_or_none()

        return catalog

