import asyncio
import logging
from sentence_transformers import SentenceTransformer

from app.shemas.catalog import CatalogCreate

# model_name = "intfloat/multilingual-e5-small"
logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name, local_files_only: bool = True):
        self.model_name = model_name
        self.local_files_only = local_files_only
        self.model: SentenceTransformer | None = None

    def get_ml_model(self) -> SentenceTransformer:
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
        model = self.get_ml_model()

        vector = model.encode(
            "passage: " + text,
            normalize_embeddings=True,
        )

        return vector.tolist()

    def ml_query(self, text: str) -> list[float]:
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




