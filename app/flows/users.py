from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import logging

from app.ai.ai_intent import AIIntentService
from app.core.states import AIBookingCreate, AiUserState, CreateUserState
from app.resources import phrases
from app.service.admin import AdminService
from app.service.booking import BookingService
from app.service.catalog import CatalogService
from app.service.faq import FaqService
from app.service.user import UserService
from app.shemas.ai import AIIntentBooking
from app.core import keyboards as kb
logger = logging.getLogger(__name__)

"""
=================================================
                   ЛОГИКА ai_user
=================================================
"""

async def ai_create_bk(message: Message,
                       state: FSMContext,
                       result: AIIntentBooking,
                       ct_sv: CatalogService,
                       bk_sv: BookingService
                       ):
    catalog_query = (result.catalog_query or "").strip()
    keywords = result.search_keywords or []

    if not catalog_query and not keywords:
        question = phrases.ask_phrase(phrases.phrases_service)
        await message.answer(question)
        await state.set_state(AIBookingCreate.ask_name)
        return

    bookings = await ct_sv.find_by_name(catalog_query)

    if not bookings:
        await message.answer("Включен умный поиск...")
        bookings = await ct_sv.embedding_search(result)

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
    await message.answer(f"Выбрана услуга: \n"
                         f"{selected.name} - {selected.price} руб / {selected.duration} мин")

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

        booking_data["time"] = time_str

    if result.comment:
        booking_data["comment"] = result.comment

    await state.update_data(**booking_data)

    is_ready = await continue_booking_flow(message, state, ct_sv)

    if not is_ready:
        return

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

async def continue_booking_flow(message: Message,
                                state: FSMContext,
                                ct_sv: CatalogService):
    data = await state.get_data()

    name = data.get('catalog_query')
    date = data.get('date')
    time = data.get('time')

    if not name:

        question = phrases.ask_phrase(phrases.phrases_service)
        await message.answer(question)
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

async def handle_faq(message: Message,
                     result: AIIntentBooking,
                     faq_sv: FaqService):
    answer = await faq_sv.find_answer(result)

    if answer:
        await message.answer(answer)
        return

    await message.answer(
        "Я пока не нашёл точный ответ на этот вопрос. "
        "Можете выбрать действие кнопками или написать администратору.",
        reply_markup=kb.main
    )

"""
=================================================
                   ЛОГИКА user
=================================================
"""

async def start_user_registration(message: Message, state: FSMContext):
    name = (message.from_user.first_name or message.from_user.username).strip()
    await state.update_data(suggested_name=name)

    await message.answer(f"Давайте познакомимся 😌\n\n"
                         f"Можно обращаться к вам как {name}?",
                         reply_markup=kb.authorization)
    await state.set_state(CreateUserState.ask_name)

async def send_booking_request(
        state: FSMContext,
        bot: Bot,
        bk_sv: BookingService,
        ad_sv: AdminService,
        comment: str
):
    data = await state.get_data()
    user_tg_id = data.get("user_tg_id")
    ct_id = data.get("ct_id")
    time_str = data.get("time")
    date_str = data.get("date")

    if not user_tg_id or not ct_id or not time_str or not date_str:
        return False, "Не хватает данных для создания заявки"

    try:

        result = await bk_sv.create_booking(
            tg_id=user_tg_id,
            ct_id=ct_id,
            date_str=date_str,
            time_str=time_str,
            comment=comment
        )

    except Exception as e:
        logger.exception(f"can't create booking tg_id={user_tg_id}, "
                         f"ct_id={ct_id}, date_str: date_str={date_str},"
                         f"time_str={time_str}, e: {e}")
        return False, "Ошибка при создании заявки"

    booking = result.booking
    user = result.user
    ct = result.ct

    text = (
        "📩 Новая заявка\n\n"
        f"👤 Пользователь: {user.name}\n"
        f"📞 Номер телефона: {user.phone}\n"
        f"🧾 Услуга: {ct.name}\n"
        f"📅 Дата: {booking.date.strftime('%d.%m.%Y')}\n"
        f"⏰ Время: {booking.time.strftime('%H:%M')}\n"
        f"💬 Комментарий: {result.comment}"
    )

    try:
        admins = await ad_sv.get_all_admin()
    except Exception as e:
        print(e)
        return False, "Ошибка при получении выборки администраторов"

    for admin in admins:
        await bot.send_message(
            chat_id=admin.tg_id,
            text=text,
            reply_markup=kb.admin_booking(booking.id)
        )

    await state.set_state(AiUserState.chatting)
    return True, "Заявка отправлена администратору"
