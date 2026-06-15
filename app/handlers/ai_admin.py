from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging

# from app.core import logger
from app.core.filtres import IsAdmin
from app.core.states import AiAdminState
from app.service.admin import AdminService
from app.ai.ai_intent import AIIntentService
from app.service.catalog import CatalogService
from app.core import keyboards as kb

router = Router()
logger = logging.getLogger(__name__)

@router.message(AiAdminState.chatting, IsAdmin())
async def ai_create_catalog(
        message: Message,
        state: FSMContext,
        ct_sv: CatalogService,
        ai_sv: AIIntentService):

    result = await ai_sv.parse_create_catalog(message.text)

    if result.intent == "unknown":
        logger.warning(
            f"Unknown admin request for ai: "
            f"user={message.from_user.id} "
            f"text={message.text}"
        )

        await message.answer(f"Я не понял ваш запрос. Можете выбрать действие кнопками",
                             reply_markup=kb.admin)

    if result.intent == "create_catalog":
        if "name" in result.missing_fields or not result.name:
            await message.answer("как вы хотите ее назвать?")
            return

        if "price" in result.missing_fields or not result.price:
            await message.answer("какую цену хотите поставить?")
            return

        if "duration" in result.missing_fields or not result.duration:
            await message.answer("Какую продолжительность поставите?")
            return

        await state.update_data(
            name=result.name,
            price=result.price,
            duration=result.duration
        )

        await message.answer(
            "Проверьте поля:\n\n"
            f"Название: {result.name}\n"
            f"Цена: {result.price} руб\n"
            f"Продолжителность услуги: {result.duration} мин",
            reply_markup=kb.confirm_ai_create_ct
        )

@router.callback_query(AiAdminState.chatting, IsAdmin(), F.data == "confirm_ai_create_ct")
async def confirm_ai_create_ct(
        callback: CallbackQuery,
        state: FSMContext,
        ct_sv: CatalogService,
        ad_sv: AdminService):
    data = await state.get_data()

    name = data.get("name")
    price_str = data.get("price")
    duration_str = data.get("duration")

    await callback.message.edit_reply_markup(reply_markup=None)

    try:
        catalog = await ct_sv.create_ct(name, price_str, duration_str, callback.from_user.id)
    except Exception:
        await callback.message.answer(f"❌ что то пошло не так при вводе данных", reply_markup=kb.admin)
        logger.exception(f"admin= {callback.from_user.id} can't create catalog")
        await state.set_state(AiAdminState.chatting)
        raise

    await callback.message.answer(f"Создана новая услуга:\n\n"
                         f"id: {catalog.id}\n"
                         f"название: {catalog.name}\n"
                         f"цена: {catalog.price} руб\n"
                         f"продолжительность: {catalog.duration} мин", reply_markup=kb.admin)
    await state.set_state(AiAdminState.chatting)

@router.callback_query(AiAdminState.chatting, IsAdmin(), F.data == "cancel_ai_create_ct")
async def cancel_ai_booking(
        callback: CallbackQuery,
        state: FSMContext):

    await state.clear()
    await callback.message.edit_text("❌ Создание услуги отменено")
    await callback.message.answer("Главное меню", reply_markup=kb.main)