import asyncio
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import List
import logging

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

async def prog():
    async with async_session() as session:
        em_sv = EmbeddingService("intfloat/multilingual-e5-small")
        ct_rp = CatalogRepos(session)
        sv = CatalogService(ct_rp=ct_rp, em_sv=em_sv)

        ct1 = CatalogCreate(
            name="Пиллинг",
            price=Decimal("1200"),
            duration=45,
            description="Процедура очищения кожи лица с удалением ороговевших клеток и улучшением состояния кожи.",
            keywords=["пиллинг", "лицо", "очищение кожи", "уход за лицом", "косметология"],
            client_phrases=[
                "хочу почистить лицо",
                "запишите на пилинг",
                "нужен уход за кожей лица",
                "хочу освежить кожу"
            ]
        )

        ct2 = CatalogCreate(
            name="Маникюр",
            price=Decimal("1450"),
            duration=60,
            description="Уход за ногтями и кожей рук с обработкой кутикулы и покрытием лаком.",
            keywords=["маникюр", "ногти", "руки", "лак", "кутикула"],
            client_phrases=[
                "хочу сделать ногти",
                "запишите на маникюр",
                "нужно привести руки в порядок",
                "хочу красивый маникюр"
            ]
        )

        ct3 = CatalogCreate(
            name="Педикюр",
            price=Decimal("1300"),
            duration=45,
            description="Уход за ногами, обработка стоп, ногтей и кутикулы.",
            keywords=["педикюр", "ноги", "стопы", "ногти", "уход за ногами"],
            client_phrases=[
                "хочу сделать ножки",
                "запишите на педикюр",
                "нужно привести ноги в порядок",
                "хочу уход за стопами"
            ]
        )

        ct4 = CatalogCreate(
            name="Наращивание ресниц",
            price=Decimal("1800"),
            duration=45,
            description="Увеличение длины и объема ресниц с помощью искусственных материалов.",
            keywords=["ресницы", "наращивание ресниц", "взгляд", "объем", "красота"],
            client_phrases=[
                "хочу длинные ресницы",
                "запишите на ресницы",
                "сделайте объемные ресницы",
                "хочу наращивание"
            ]
        )

        ct5 = CatalogCreate(
            name="стрижка мужская",
            price=Decimal("1000"),
            duration=50,
            description="Мужская стрижка машинкой и ножницами с оформлением прически.",
            keywords=["стрижка", "волосы", "барбер", "мужская стрижка", "парикмахер"],
            client_phrases=[
                "хочу подстричься",
                "нужно укоротить волосы",
                "запишите на мужскую стрижку",
                "сделайте мне прическу"
            ]
        )

        ct6 = CatalogCreate(
            name="Массаж",
            price=Decimal("1600"),
            duration=90,
            description="Расслабляющий массаж тела для снятия напряжения и усталости.",
            keywords=["массаж", "спина", "расслабление", "тело", "мышцы"],
            client_phrases=[
                "болит спина",
                "хочу массаж",
                "нужно расслабиться",
                "запишите на массаж"
            ]
        )

        ct7 = CatalogCreate(
            name="стрижка женская",
            price=Decimal("2600"),
            duration=50,
            description="Женская стрижка с подбором формы и укладкой волос.",
            keywords=["стрижка", "волосы", "женская стрижка", "укладка", "парикмахер"],
            client_phrases=[
                "хочу изменить прическу",
                "нужно подстричь волосы",
                "запишите на женскую стрижку",
                "хочу новую стрижку"
            ]
        )

        ct8 = CatalogCreate(
            name="Окрашивание волос женское",
            price=Decimal("3600"),
            duration=60,
            description="Изменение цвета волос с использованием профессиональных красителей.",
            keywords=["окрашивание", "волосы", "краска", "блонд", "цвет волос"],
            client_phrases=[
                "хочу покрасить волосы",
                "изменить цвет волос",
                "запишите на окрашивание",
                "хочу стать блондинкой"
            ]
        )

        ct9 = CatalogCreate(
            name="Уход за ресницами",
            price=Decimal("2200"),
            duration=50,
            description="Укрепление, восстановление и уход за натуральными ресницами.",
            keywords=["ресницы", "ламинирование", "уход", "восстановление", "взгляд"],
            client_phrases=[
                "хочу красивые ресницы",
                "нужен уход за ресницами",
                "запишите на ламинирование",
                "укрепить ресницы"
            ]
        )

        ct10 = CatalogCreate(
            name="Мужское окрашивание волос",
            price=Decimal("2300"),
            duration=70,
            description="Окрашивание мужских волос для смены цвета или маскировки седины.",
            keywords=["мужское окрашивание", "волосы", "седина", "краска", "цвет волос"],
            client_phrases=[
                "хочу покрасить волосы",
                "закрасить седину",
                "изменить цвет волос",
                "запишите на окрашивание"
            ]
        )

        cts = CatalogList(item=[ct1, ct2, ct3, ct4, ct5,
                                ct6, ct7, ct8, ct9, ct10])
        n = 1
        for c in cts.item:

            embedding = await em_sv.embed_catalog(c)

            new_ct = await ct_rp.create_ct(c, embedding)

            print("ct: ", n)
            n+=1

        await session.commit()

if __name__ == "__main__":
    asyncio.run(prog())