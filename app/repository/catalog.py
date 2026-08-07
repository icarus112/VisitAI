from typing import List

from sqlalchemy import select, func, desc

from app.shemas.catalog import CatalogCreate, CatalogResponse
from app.database import Catalog


class CatalogRepos:
    def __init__(self, session):
        self.session = session

    async def create_ct(self, add_catalog: CatalogCreate, embedding: list[float]) -> CatalogResponse:
        catalog = Catalog(**add_catalog.model_dump(), embedding=embedding)

        self.session.add(catalog)
        await self.session.flush()
        await self.session.refresh(catalog)

        result = CatalogResponse.model_validate(catalog)

        return result

    async def get_all(self) -> List[Catalog]:
        stmt = (select(Catalog).order_by(Catalog.id))

        results = await self.session.execute(stmt)
        catalogs = results.scalars().all()
        return catalogs

    async def count_ct(self) -> int:
        stmt = (select(func.count(Catalog.id)))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_ct_page(self, page: int, per_page: int = 5) -> list[Catalog]:
        offset = page * per_page

        stmt = (
            select(Catalog)
            .order_by(Catalog.id)
            .limit(per_page)
            .offset(offset) # пропустить заданное кол-во строк перед работой
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_ct_by_id(self, id: int) -> Catalog:
        stmt = (select(Catalog)
                .where(Catalog.id == id))

        result = await self.session.execute(stmt)
        catalog = result.scalar_one_or_none()
        return catalog

    async def find_ilike(self, query: str) -> List[Catalog]:
        stmt = (select(Catalog)
                .where(Catalog.name.ilike( f"%{query}%"))
                )
        result = await self.session.execute(stmt)
        catalogs = list(result.scalars().all())

        return catalogs

# вернут 5 самых схожих названий через similarity
    async def find_name_fuzzy(self, query: str) -> List[Catalog]:
        similarity = func.similarity(Catalog.name, query)

        stmt = (
            select(Catalog)
            .where(similarity > 0.3)
            .order_by(desc(similarity))
            .limit(5)
            )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def embedding_search(self,
                               query_vector: list[float],
                               limit: int = 5):
        distance = Catalog.embedding.cosine_distance(query_vector).label("distance")

        stmt = (
            select(Catalog, distance)
            .where(Catalog.embedding.is_not(None))
            .order_by(distance)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return result.all()