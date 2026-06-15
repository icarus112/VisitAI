import asyncio
import math
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import List
import logging

from app.repository import catalog
from app.repository.catalog import CatalogRepos
from app.service.embedding import EmbeddingService as em_sv, EmbeddingService
from app.shemas.ai import AIIntentBooking
from app.shemas.catalog import CatalogCreate, CatalogResponse, CatalogList
from database.async_engine import async_session

from database.models import Catalog

logger = logging.getLogger(__name__)

class CatalogService:
    def __init__(self, ct_rp: CatalogRepos, em_sv: EmbeddingService):
        self.ct_rp = ct_rp
        self.em_sv = em_sv

    async def str_to_decimal(self, value) -> Decimal:
        if value is None:
            logger.warning("get value None, can't convert to Decimal")
            raise ValueError("Цена не может быть пустой")

        if isinstance(value, Decimal):
            decimal_value = value

        else:
            text = str(value).strip().replace(",", ".")

            try:
                decimal_value = Decimal(text)
            except InvalidOperation:
                logger.warning(" invalid operation, can't convert to Decimal")
                raise ValueError("Цена должна быть числом, например 1500 или 1500.5")

        if decimal_value < 0:
            raise ValueError("Число должны быть положительными или 0")

        return decimal_value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)


    async def create_ct(self, name, price, duration, ad_tg_id, ai_res) -> CatalogResponse:
        if not name:
            logger.warning("get ct_name None, can't create catalog")
            raise ValueError("Название не может быть пустым")

        if ai_res is None:
            logger.warning("get ai_res None, can't create catalog")
            raise ValueError("Произашла ошибка при создании доп полей(descriptions and etc.)")

        price = await self.str_to_decimal(price)

        try:
            duration = int(duration)
        except Exception:
            logger.warning("get invalid duration, can't create catalog")
            raise ValueError("Длительность должна быть числом, например 30")

        if duration <= 0:
            logger.warning("get invalid duration, can't create catalog")
            raise ValueError("Длительность должна быть больше 0")

        ct_data = CatalogCreate(
            name=name,
            price=price,
            duration=duration,
            description=ai_res.description,
            keywords = ai_res.keywords,
            client_phrases = ai_res.client_phrases
        )

        embedding = await self.em_sv.embed_catalog(ct_data)

        try:
            new_ct = await self.ct_rp.create_ct(ct_data, embedding)
        except Exception:
            logger.warning("create new catalog failed, can't create catalog")
            raise

        logger.info(f"created new catalog [name={new_ct.name}] by admin id={ad_tg_id}")
        return new_ct

    async def get_all(self) -> List[Catalog]:
        catalogs = await self.ct_rp.get_all()
        if not catalogs:
            logger.warning("can't get all catalogs")
            raise ValueError("ничего не найдено")

        return catalogs

    async def page_data(self, page: int, per_page: int = 5 ):

        total = await self.ct_rp.count_ct() #общее кол услуг

        if total == 0:
            return [], 0, 0

        # math.ceil - округляет число вверх
        total_pages = math.ceil(total / per_page)
        #total_pages - кол-во страниц(по умолчанию 5 услуг в каждой странице)

        if page < 0:
            page = 0

        if page >= total_pages:
            page = total_pages - 1

        catalogs = await self.ct_rp.get_ct_page(page, per_page)

        return catalogs, page, total_pages

    async def get_ct_by_id(self, ct_id: int) -> Catalog:
        selected = await self.ct_rp.get_ct_by_id(ct_id)

        return selected

    async def find_by_name(self, query: str) -> List[Catalog]:

        cts = await self.ct_rp.find_ilike(query)
        if not cts:
            cts = await self.ct_rp.find_name_fuzzy(query)

        return cts

    async def embedding_search(self, result: AIIntentBooking):
        name = result.catalog_query or ""
        keywords = result.search_keywords or []

        if not name and not keywords:
            return []

        query_vector = await self.em_sv.embed_by_intent(name, keywords)
        rows = await self.ct_rp.embedding_search(query_vector, limit=5)

        results = [catalog for catalog, distance in rows if distance <= 0.4]

        return results

    async def embedding_search_by_name(self, catalog_query: str):
        name = catalog_query

        if not name:
            return []

        query_vector = await self.em_sv.embed_by_intent(name, [])
        rows = await self.ct_rp.embedding_search(query_vector, limit=5)

        results = [catalog for catalog, distance in rows if distance <= 0.4]

        return results