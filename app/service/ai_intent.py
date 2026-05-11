import json
from openai import AsyncOpenAI
from app.shemas.ai import AIIntentBooking

class AIIntentService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com")

    async def parse_user_message(self, text: str | None) -> AIIntentBooking:
        prompt = f"""
Ты помощник Telegram-бота для записи клиентов.

Твоя задача - понять сообщение пользователя и вернуть ТОЛЬКО JSON.

Возможные intent:
- create_booking
- check_bookings
- cancel_booking
- recommend_catalog
- faq
- unknown

Поля:
- intent
- catalog_query
- date
- time
- comment
- missing_fields
- confidence

Правила:
- date только в формате DD.MM.YYYY
- time только HH:MM
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
            print("raw_text:", raw_text)
            print("AI parse error: ", e)

            return AIIntentBooking(
                intent="unknown",
                confidence=0.0
            )

    async def parse_create_catalog(self, text: str | None) -> AIIntentBooking:
        prompt = f"""
Ты помощник Telegram-бота для записи клиентов.

Твоя задача - обработать текст от сотрудника для создания сущности и вернуть ТОЛЬКО JSON.

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
            print("raw_text:", raw_text)
            print("AI parse error: ", e)

            return AIIntentBooking(
                intent="unknown",
                confidence=0.0
            )


