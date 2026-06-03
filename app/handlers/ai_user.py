from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging

# from app.core import logger
from app.core.states import CreateUserState, AiUserState, AIBookingCreate
from app.handlers.record import send_booking_request
from app.service.admin import AdminService
from app.core.ai_intent import AIIntentService
from app.service.booking import BookingService
from app.service.catalog import CatalogService
from app.core import keyboards as kb
from app.service.user import UserService
from app.resources import phrases

router = Router()
logger = logging.getLogger(__name__)

async def continue_booking_flow(message: Message,
                                state: FSMContext,
                                ct_sv: CatalogService):
    data = await state.get_data()

    name = data.get('catalog_query')
    date = data.get('date')
    time = data.get('time')

    if not name:
        catalogs = await ct_sv.get_all()

        question = phrases.ask_phrase(phrases.phrases_service)
        await message.answer(question,
        reply_markup=kb.catalog_keyboard(catalogs))
        await state.set_state(AIBookingCreate.ask_name)
        return False

    if not date:

        question = phrases.ask_phrase(phrases.phrases_date)

        await message.answer(question)
        await state.set_state(AIBookingCreate.ask_date)
        return False

    if not time:

        question = phrases.ask_phrase(phrases.phrases_time)

        await message.answer(question)
        await state.set_state(AIBookingCreate.ask_time)
        return False

    return True

@router.message(AIBookingCreate.ask_date)
async def ask_booking_date(message: Message, state: FSMContext, ct_sv: CatalogService):
    await state.update_data(date=message.text)

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


    time_str = time.strftime('%H:%M')
    await state.update_data(time=time_str)

    is_ready = await continue_booking_flow(message, state, ct_sv)

    if is_ready:
        await state.set_state(AiUserState.chatting)
        await confirm_booking(message, state)

async def confirm_booking(message: Message, state: FSMContext):
    data = await state.get_data()

    name = data.get('catalog_query')
    date = data.get('date')
    time = data.get('time')
    comment = data.get('comment')

    await message.answer(
        f"Проверьте запись:\n\n"
        f"Услуга: {name}\n"
        f"Дата: {date}\n"
        f"Время: {time}\n"
        f"Комментарий: {comment or '-'}",
        reply_markup=kb.confirm_ai_booking
    )

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
        bk_sv: BookingService):

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
        logger.warning(
            f"Unknown user request for ai: "
            f"user= {message.from_user.id} "
            f"text= {message.text}"
        )
        await message.answer("Я не понял ваш запрос.Можете выбрать действие кнопками",
                             reply_markup=kb.main)
        return

    if result.intent == "create_booking":

        catalog_query = result.catalog_query or ""
        bookings = await ct_sv.find_by_name(catalog_query)

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

        booking_data = {}

        if result.date:
            booking_data["date"] = result.date

        if result.time:
            time_str = result.time

            try:
                time = bk_sv.parse_time(time_str)

            except ValueError:
                logger.exception(f"could not parse time={time_str}")
                await message.answer("вы ввели не правильное время попробуйте заново", reply_markup=kb.main)
                await state.clear()
                await state.set_state(AiUserState.chatting)

            time_str = time.strftime('%H:%M')

            booking_data["time"] = result.time

        if result.comment:
            booking_data["comment"] = result.comment

        await state.update_data(**booking_data)

        is_ready = await continue_booking_flow(message, state, ct_sv)

        if not is_ready:
            return

        await state.set_state(AiUserState.chatting)
        await confirm_booking(message, state)

@router.callback_query(AIBookingCreate.ask_name, F.data.startswith("catalog:"))
async def bk_select(callback: CallbackQuery, state: FSMContext,
                    ct_sv: CatalogService):
    ct_id = int(callback.data.split(":")[1].strip())

    await callback.answer()

    selected = await ct_sv.get_ct_by_id(ct_id)
    if selected:
        await callback.message.edit_text(f"вы выбрали \n{selected.name} - "
                                         f"{selected.price} руб / {selected.duration} мин")

        await state.update_data(
            user_tg_id=callback.from_user.id,
            ct_id=selected.id,
            catalog_query=selected.name
        )

        is_ready = await continue_booking_flow(callback.message, state, ct_sv)

        if not is_ready:
            return

        await state.set_state(AiUserState.chatting)
        await confirm_booking(callback.message, state)

    else:
        logger.warning(f"can't find ct_id={ct_id}")
        await callback.message.edit_text("Услуга не найдена")
        await state.clear()


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

    await state.set_state(AiUserState.chatting)
    await callback.message.edit_text("❌ Создание записи отменено")
    logger.info(f"canceled booking| user_id= {callback.from_user.id}, ct_name= {catalog_query}")
    await callback.message.answer("Главное меню", reply_markup=kb.main)

