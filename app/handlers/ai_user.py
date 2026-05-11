from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.core.states import CreateUserState, AiUserState
from app.handlers.record import send_booking_request
from app.service.admin import AdminService
from app.service.ai_intent import AIIntentService
from app.service.booking import BookingService
from app.service.catalog import CatalogService
from app.core import keyboards as kb
from app.service.user import UserService
from database.models import Catalog

router = Router()

@router.message(AiUserState.chatting)
async def ai_record_handler(
        message: Message,
        state: FSMContext,
        ai_sv: AIIntentService,
        ct_sv: CatalogService,
        us_sv: UserService):

    user = await us_sv.get_by_tg_id(message.from_user.id)
    if not user:
        #  у юзера может не быть юзернейма
        name = message.from_user.username or message.from_user.first_name
        await state.update_data(suggested_name=name)

        await message.answer(f"Давайте познакомимся 😌\n\n"
                             f"Можно обращаться к вам как {name}?",
                             reply_markup=kb.authorization)
        await state.set_state(CreateUserState.ask_name)  # продолжение в файле handler/user.py
        return

    result = await ai_sv.parse_user_message(message.text)

    if result.intent == "unknown":
        await message.answer("Я не понял ваш запрос.Можете выбрать действие кнопками",
                             reply_markup=kb.main)
        return

    if result.intent == "create_booking":
        if "catalog" in result.missing_fields or not result.catalog_query:
            await message.answer("На какую услугу хотите записаться?")
            return

        if "date" in result.missing_fields or not result.date:
            await message.answer("На какую дату вы хотите сделать запись?")
            return

        if "time" in result.missing_fields or not result.time:
            await message.answer("На какое время вы хотите сделать запись?")
            return

        catalog = await ct_sv.find_by_name(result.catalog_query)
        user_tg_id =message.from_user.id

        if not catalog:
            await message.answer("Я не нашёл такую услугу. Выберите услугу из списка.")
            return

        await state.update_data(
            user_tg_id=user_tg_id,
            ct_id=catalog.id,
            date=result.date,
            time=result.time,
            comment=result.comment or "-"
        )

        await message.answer(
            f"Проверьте запись:\n\n"
            f"Услуга: {catalog.name}\n"
            f"Дата: {result.date}\n"
            f"Время: {result.time}\n"
            f"Комментарий: {result.comment or '-'}",
            reply_markup=kb.confirm_ai
        )

@router.callback_query(F.data == "confirm_ai_booking")
async def confirm_ai_booking(
        callback: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        bk_sv: BookingService,
        ad_sv: AdminService):
    data = await state.get_data()

    ok, text = await send_booking_request(
        state=state,
        bot=bot,
        bk_sv=bk_sv,
        ad_sv=ad_sv,
        comment=data.get('comment', '-')
    )

    await callback.message.edit_text(text)
    await state.clear()

@router.callback_query(F.data == "cancel_ai_booking")
async def cancel_ai_booking(
        callback: CallbackQuery,
        state: FSMContext):

    await state.clear()
    await callback.message.edit_text("❌ Создание записи отменено")
    await callback.message.answer("Главное меню", reply_markup=kb.main)

