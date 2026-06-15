import json
from openai import AsyncOpenAI
from app.shemas.ai import AIIntentBooking, AIIntentCatalog, AICatalogDescription
from datetime import datetime
import logging

today = datetime.today()
logger = logging.getLogger(__name__)


class AIIntentService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com")

    async def parse_user_message(self, text: str | None) -> AIIntentBooking:
        if not text or not text.strip():
            return AIIntentBooking(
                intent="unknown",
                confidence=0.0
            )

        prompt = f"""
Ты помощник Telegram-бота для записи клиентов. Сегодня число {today.strftime('%d.%m.%Y')}

Твоя задача - понять сообщение пользователя и вернуть СТРОГО валидный JSON.
Не используй markdown, комментарии, пояснения или текст до/после JSON.

Возможные intent:
- create_booking - пользователь хочет записаться на услугу
- check_bookings - пользователь хочет посмотреть свои записи
- cancel_booking - пользователь хочет отменить запись
- recommend_catalog - пользователь просит посоветовать услугу
- faq - пользователь задаёт общий вопрос
- unknown - намерение непонятно

Если пользователь спрашивает цену, длительность или описание конкретной услуги, используй recommend_catalog, а не faq.
Если пользователь спрашивает общие условия сервиса, используй faq.

Всегда возвращай JSON с такими полями:
- intent
- catalog_query
- search_keywords
- date
- time
- comment
- missing_fields
- confidence

Поля:
- intent
- catalog_query
- search_keywords
- date
- time
- comment
- missing_fields
- confidence

Если пользователь хочет записаться, но не указал конкретную услугу, НЕ придумывай catalog_query.
В этом случае catalog_query = null, search_keywords = [], а в missing_fields добавь "catalog_query".
Слова "записаться", "приём", "к вам", "услуга" не являются названием услуги.

Правила для catalog_query:
- это короткая фраза, описывающая нужную услугу
- убирай дату, время, приветствия и лишний текст
- пример: "хочу завтра в 15 сделать ножки" -> "педикюр"
- пример: "нужно подстричься и бороду" -> "стрижка и борода"

Правила для search_keywords:
- всегда список
- для create_booking: список из 1-5 слов или коротких фраз для поиска услуги
- для recommend_catalog: список из 1-5 слов или коротких фраз для поиска услуги
- для faq: список из 1-5 слов или коротких фраз для поиска FAQ-ответа
- не добавляй дату и время
- не добавляй лишние слова типа "хочу", "можно", "запишите", "скажите", "подскажите"

Правила для date:
- только формат DD.MM.YYYY
- относительные даты преобразуй в точную дату
- "сегодня" = {today.strftime('%d.%m.%Y')}
- если даты нет, верни null

Правила для time:
- только формат HH:MM
- если время неточное, например "вечером", "после обеда", "утром", верни null и добавь "time" в missing_fields
- если времени нет, верни null

Правила для missing_fields:
- всегда список
- для create_booking добавь недостающие поля: "catalog_query", "date", "time"
- для других intent верни []

Правила для comment:
- для create_booking: сюда помещай дополнительные пожелания клиента, которые не являются услугой, датой или временем
- для faq: сюда помещай исходный вопрос пользователя или его краткую суть
- для recommend_catalog: сюда помещай исходный вопрос пользователя или его краткую суть
- для unknown: сюда можно поместить исходный текст пользователя
- если комментария нет, верни null

Правила для confidence:
- число от 0 до 1
- если intent понятен уверенно, ставь 0.8-1
- если есть сомнения, ставь 0.4-0.7
- если почти ничего не понятно, ставь 0-0.3

Пример create_booking:
{{
  "intent": "create_booking",
  "catalog_query": "педикюр",
  "search_keywords": ["педикюр", "ноги", "стопы", "ногти"],
  "date": "{today.strftime('%d.%m.%Y')}",
  "time": "15:00",
  "comment": null,
  "missing_fields": [],
  "confidence": 0.95
}}

Правила для FAQ:
- intent = "faq", если пользователь задаёт общий вопрос о сервисе, условиях, адресе, графике, оплате, отмене, переносе, мастерах, правилах
- при faq всегда возвращай catalog_query = null
- при faq всегда возвращай date = null
- при faq всегда возвращай time = null
- при faq всегда возвращай missing_fields = []
- при faq в comment помещай исходный вопрос пользователя или его краткую суть
- при faq в search_keywords помещай 1-5 ключевых слов для поиска ответа в FAQ
- примеры ключевых слов для faq: "график", "адрес", "оплата", "отмена", "перенос", "мастер", "правила", "контакты"

Пример FAQ:
"Где вы находитесь?" ->
{{
  "intent": "faq",
  "catalog_query": null,
  "search_keywords": ["адрес", "локация", "местоположение"],
  "date": null,
  "time": null,
  "comment": "Где вы находитесь?",
  "missing_fields": [],
  "confidence": 0.95
}}

Сообщение пользователя:
{text}
"""
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "Ты возвращаешь только JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        raw_text = response.choices[0].message.content.strip()

        raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(raw_text)
            return AIIntentBooking(**data)

        except Exception as e:
            logger.exception("raw_text: %s", raw_text)
            logger.exception("AI parse error: %s", e)

            return AIIntentBooking(
                intent="unknown",
                confidence=0.0
            )

    async def parse_create_catalog(self, text: str | None) -> AIIntentCatalog:
        if not text or not text.strip():
            return AIIntentCatalog(
                intent="unknown",
                confidence=0.0
            )

        prompt = f"""
Ты помощник Telegram-бота для записи клиентов.

Твоя задача - обработать текст от сотрудника для создания сущности.
Верни СТРОГО валидный JSON без markdown, без комментариев, без текста до или после JSON.

Возможные intent:
- create_catalog
- check_catalog
- edit_price
- edit_duration
- unknown

Поля:
- name
- price
- duration
- missing_fields
- confidence

Правила:
- price только целое число
- duration только целое число
- missing_fields всегда список
- confidence число от 0 до 1
- никакого текста кроме JSON

Сообщение пользователя:
{text}
        """
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "Ты возвращаешь только валидный JSON. Без markdown, без пояснений."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        raw_text = response.choices[0].message.content.strip()

        if not raw_text:
            logger.error("AI returned empty response")
            return None

        raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(raw_text)
            return AIIntentCatalog(**data)

        except Exception as e:
            logger.exception("raw_text: %s", raw_text)
            logger.exception("AI parse error: %s", e)

            return AIIntentCatalog(
                intent="unknown",
                confidence=0.0
            )

    async def create_description(self, name: str | None) -> AICatalogDescription | None:
        if not name or not name.strip():
            return None

        prompt = f"""
        Ты помощник Telegram-бота для записи клиентов.
        Твоя задача - обработать название услуги от сотрудника для создания данные для semantic embedding поиска услуги.
        Верни СТРОГО валидный JSON без markdown, без комментариев, без текста до или после JSON.

        JSON должен иметь ровно такие поля:
        - description: string
        - keywords: array of strings
        - client_phrases: array of strings
        
        Что нужно сгенерировать:
        1. description - короткое понятное описание услуги на русском языке, 1 предложение.
        2. keywords - 5-10 ключевых слов или фраз, по которым клиент может искать эту услугу.
        3. client_phrases - 3-7 фраз, как обычный клиент может попросить эту услугу не используя название услуги в чате.

        
        Пример вывода для name: "мужская стрижка": 
        {{
          "description": "Мужская стрижка машинкой и ножницами, оформление формы, укладка.",
          "keywords": ["стрижка", "волосы", "барбер", "мужская стрижка"],
          "client_phrases": [
            "хочу подстричься",
            "запишите меня на стрижку",
            "нужно волосы подровнять"
          ]
        }}

        Правила:
        - Не выдумывай цену.
        - Не выдумывай длительность.
        - Не добавляй поля, которых нет в схеме.
        - Не возвращай markdown.
        - Если название услуги слишком непонятное, всё равно сделай лучший возможный вариант.
        - Все значения должны быть на русском языке.

        Сообщение пользователя:
        {name}
                """
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "Ты возвращаешь только JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        raw_text = response.choices[0].message.content.strip()


        if not raw_text:
            logger.error("AI returned empty response")
            return None

        raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(raw_text)
            return AICatalogDescription(**data)

        except Exception as e:
            logger.exception("raw_text: %s", raw_text)
            logger.exception("AI parse error: %s", e)




