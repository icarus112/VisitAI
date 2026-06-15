from app.shemas.ai import AIIntentBooking


class FaqService:
    def __init__(self, faq_rp):
        self.faq_rp = faq_rp

    async def find_answer(self, result: AIIntentBooking) -> str | None:
        if result.intent != "faq":
            return None

        query = f"{result.comment or ''}  {" ".join(result.search_keywords) or ''}".strip()

        faq = await self.faq_rp.find_answer(query)

        if not faq:
            return None
        else:
            return faq.answer
