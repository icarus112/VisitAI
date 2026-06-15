from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging

# from app.core import logger
from app.core.states import CreateUserState, AiUserState, AIBookingCreate
from app.flows.users import continue_booking_flow, confirm_booking, start_user_registration, ai_create_bk, handle_faq
from app.handlers.record import send_booking_request
from app.service.admin import AdminService
from app.ai.ai_intent import AIIntentService
from app.service.booking import BookingService
from app.service.catalog import CatalogService
from app.core import keyboards as kb
from app.service.faq import FaqService
from app.service.user import UserService
from app.resources import phrases
from app.shemas.ai import AIIntentBooking

router = Router()
logger = logging.getLogger(__name__)

@router.message(AIBookingCreate.ask_date)
async def ask_booking_date(message: Message, state: FSMContext,
                           ct_sv: CatalogService,
                           bk_sv: BookingService):
    date_str = message.text
    date = bk_sv.parse_date(date_str)

    await state.update_data(date=date)

    is_ready = await continue_booking_flow(message, state, ct_sv)

    if is_ready:
        await state.set_state(AiUserState.chatting)
        await confirm_booking(message, state)


@router.message(AIBookingCreate.ask_time)
async def ask_booking_time(message: Message,
                           state: FSMContext,
                           ct_sv: CatalogService,
                           bk_sv: BookingService):
    time_str = message.text

    try:
        time = bk_sv.parse_time(time_str)

    except ValueError:
        await message.answer("вы ввели не правильное время попробуйте заново", reply_markup=kb.main)
        await state.clear()
        await state.set_state(AiUserState.chatting)
        return


    time_str = time.strftime('%H:%M')
    await state.update_data(time=time_str)

    is_ready = await continue_booking_flow(message, state, ct_sv)

    if is_ready:
        await state.set_state(AiUserState.chatting)
        await confirm_booking(message, state)

@router.message(AIBookingCreate.ask_name)
async def ask_booking_name(message: Message,
                           state: FSMContext,
                           ct_sv: CatalogService):

    catalog_query = message.text.strip()
    if not message.text or message.text.strip():
        await message.answer("прошу повторите запрос заново", reply_markup=kb.main)
        await state.clear()
        await state.set_state(AiUserState.chatting)
        return

    await message.answer("простой поиск...")
    bookings = await ct_sv.find_by_name(catalog_query)

    if not bookings:
        await message.answer("Включен умный поиск...")
        bookings = await ct_sv.embedding_search_by_name(catalog_query)

        if not bookings:
            logger.info(
                f"can't find catalog for name: {catalog_query}"
            )
            await message.answer("Я не нашёл такую услугу. Выберите услугу из списка", reply_markup=kb.main)
            return

    if len(bookings) > 1:
        question = phrases.ask_phrase(phrases.similar_services)

        await message.answer(
            question,
            reply_markup=kb.catalog_keyboard(bookings)
        )

        await state.set_state(AIBookingCreate.ask_name)
        return

    selected = bookings[0]

    await state.update_data(
        user_tg_id=message.from_user.id,
        ct_id=selected.id,
        catalog_query=selected.name
    )

    is_ready = await continue_booking_flow(message, state, ct_sv)

    if is_ready:
        await state.set_state(AiUserState.chatting)
        await confirm_booking(message, state)

''' на будущее при create_booking:
1. поиск услуги, есть ли она
2. выбрать услугу
3. проверка missing_fields
4. собираем поля если их не ввели
5. отправляем админу
'''

@router.message(AiUserState.chatting)
async def ai_record_handler(
        message: Message,
        state: FSMContext,
        ai_sv: AIIntentService,
        ct_sv: CatalogService,
        us_sv: UserService,
        bk_sv: BookingService,
        faq_sv: FaqService):

    user = await us_sv.get_by_tg_id(message.from_user.id)
    if not user:
        #  у юзера может не быть юзернейма
        await start_user_registration(message, state)
        return

    result = await ai_sv.parse_user_message(message.text)

    if result.intent == "unknown":
        logger.warning(
            f"Unknown user request for ai: "
            f"user= {message.from_user.id} "
            f"text= {message.text}"
        )
        await message.answer("Я не понял ваш запрос.Можете выбрать действие кнопками",
                             reply_markup=kb.main)
        return

    if result.intent == "create_booking":
        await ai_create_bk(message, state, result,
                       ai_sv, ct_sv, us_sv, bk_sv)
        return

    if result.intent == "faq":
        await handle_faq(message, result, faq_sv)
        return

@router.callback_query(AIBookingCreate.ask_name, F.data.startswith("catalog:"))
async def choose_catalog(callback: CallbackQuery,
                         state: FSMContext,
                         ct_sv: CatalogService):

    catalog_id = int(callback.data.split(":")[1])
    catalog = await ct_sv.get_ct_by_id(catalog_id)

    await callback.message.edit_reply_markup(reply_markup=None)

    await state.update_data(
        user_tg_id=callback.from_user.id,
        ct_id=catalog.id,
        catalog_query=catalog.name
    )

    await callback.message.answer(f"Выбрана услуга: {catalog.name}")

    is_ready = await continue_booking_flow(callback.message, state, ct_sv)

    if is_ready:
        await state.set_state(AiUserState.chatting)
        await confirm_booking(callback.message, state)


@router.callback_query(AiUserState.chatting, F.data == "confirm_ai_booking")
async def confirm_ai_booking(
        callback: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        bk_sv: BookingService,
        ad_sv: AdminService):
    data = await state.get_data()
    catalog_query = data.get('catalog_query')

    ok, text = await send_booking_request(
        state=state,
        bot=bot,
        bk_sv=bk_sv,
        ad_sv=ad_sv,
        comment=data.get('comment', '-')
    )

    await callback.message.edit_text(text)

@router.callback_query(AiUserState.chatting, F.data == "cancel_ai_booking")
async def cancel_ai_booking(
        callback: CallbackQuery,
        state: FSMContext):

    data = await state.get_data()
    catalog_query = data.get('catalog_query')

    await state.clear()
    await state.set_state(AiUserState.chatting)
    await callback.message.edit_text("❌ Создание записи отменено")
    logger.info(f"canceled booking| user_id= {callback.from_user.id}, ct_name= {catalog_query}")
    await callback.message.answer("Главное меню", reply_markup=kb.main)