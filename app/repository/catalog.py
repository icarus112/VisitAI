from sqlalchemy.ext.asyncio import AsyncSession

from app.shemas.catalog import CatalogCreate
from database.models import Catalog


class CatalogRepos:
    def __init__(self, session):
        self.session = session

    async def create_ct(self, add_catalog: CatalogCreate) -> Catalog:
        catalog = Catalog(**add_catalog.model_dump())

        self.session.add(catalog)
        await self.session.flush()
        await self.session.refresh(catalog)
        return catalog

