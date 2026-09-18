import asyncio
import logging
from sentence_transformers import SentenceTransformer
# SentenceTransformer - работает на основе загружаемой ml модели и привращяет текст в массив чисел

from app.shemas.catalog import CatalogCreate

# model_name = "intfloat/multilingual-e5-small"
logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name, local_files_only: bool = True):
        self.model_name = model_name
        self.local_files_only = local_files_only # использовать ли только локальные модели
        self.model: SentenceTransformer | None = None # она создаcтся при первом вызове SentenceTransformer

    def get_ml_model(self) -> SentenceTransformer:
        # она создаст готовую модель
        if self.model is None:
            self.model = SentenceTransformer(self.model_name,
                local_files_only=self.local_files_only,)

        return self.model

#     query: вопрос / запрос
#     passage: текст - кандидат
#
# ml_passage: используется для поулучения вектора для сохранения в БД
# ml_query: используется для получение вектора что бы сравнить его потом c passage


    def ml_passage(self, text: str) -> list[float]:
        # получает название услуги и превращяет ее в массив чисел
        model = self.get_ml_model()

        vector = model.encode(
            "passage: " + text,
            normalize_embeddings=True, # нормалалиозовать вектор что бы длина была равно 1, для вычислений это важно
        )

        return vector.tolist()

    def ml_query(self, text: str) -> list[float]:
        # принимает клиентский текст и превращяет ее в массив чисел
        model = self.get_ml_model()

        vector = model.encode(
            "query: " + text,
            normalize_embeddings=True,
        )

        return vector.tolist()

    async def ml_passage_async(self, text: str) -> list[float]:
        return await asyncio.to_thread(self.ml_passage, text)

    async def ml_query_async(self, text: str) -> list[float]:
        return await asyncio.to_thread(self.ml_query, text)

    async def embed_catalog(self, ct: CatalogCreate) -> list[float] :
        parts = [
            f"Название услуги: {ct.name}",
            f"Описание услуги: {ct.description}",
            f"Ключевые слова: {', '.join(ct.keywords)}",
            f"Как клиенты могут написать {'; '.join(ct.client_phrases)}",
        ]

        text = "\n".join(parts)
        return await self.ml_passage_async(text)

    async def embed_by_intent(self, name: str, keywords: list[str]) -> list[float] :
        keywords = keywords or []
        parts = []

        if name:
            parts.append(f"Запрос услуги: {name}")

        if keywords:
            parts.append(f"Ключевые слова: {', '.join(keywords)}")

        text = "\n".join(parts)
        return await self.ml_query_async(text)




