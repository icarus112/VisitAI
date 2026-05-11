from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.core.filtres import IsAdmin
from app.service.ai_intent import AIIntentService
from app.service.catalog import CatalogService

router = Router()

@router.message(IsAdmin())
async def ai_create_catalog(
        message: Message,
        state: FSMContext,
        ct_sv: CatalogService,
        ai_sv: AIIntentService):

    result = await ai_sv.parse_create_catalog(message.text)