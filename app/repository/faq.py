from idlelib import search

from sentence_transformers.util import similarity
from sqlalchemy import func, select, desc, cast, Text
from sqlalchemy.ext.asyncio import result

from app.shemas.faq import FaqCreate
from database.models import Faq


class FAQRepos:
    def __init__(self, session):
        self.session = session

    async def create_faq(self, faq: FaqCreate):
        search_text = f"{faq.question} {' '.join(faq.keywords)}".strip()
        faq = Faq(**faq.model_dump(), search_text=search_text)

        self.session.add(faq)
        await self.session.flush()
        await self.session.refresh(faq)

        return faq

    async def find_answer(self, query: str) -> Faq:

        similarity = func.similarity(
            Faq.search_text,
            cast(query, Text) #явное приведение типа в нужный 
        )

        stmt = (
            select(Faq)
            .where(similarity > 0.3)
            .order_by(desc(similarity))
            .limit(1)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

