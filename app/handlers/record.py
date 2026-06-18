from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, callback_query
import logging

from app.core import keyboards as kb
from app.core.states import CreateUserState, Requests, AiUserState, RemovingBooking
from app.flows.users import start_user_registration, send_bk_remove
from app.resources import phrases
from app.service.admin import AdminService
from app.service.booking import BookingService
from app.service.catalog import CatalogService
from app.service.user import UserService
from app.flows.users import send_booking_request

router = Router()
logger = logging.getLogger(__name__)
#проверить ввод даты
#проверить без комента
'''
========================================================================================
                                     ДОБАВИТЬ ЗАПИСЬ
========================================================================================
'''

@router.message(F.text == "✏️Добавить запись")
async def add_record(message: Message, state: FSMContext,
                     us_sv: UserService):

    await state.clear()

    user = await us_sv.get_by_tg_id(message.from_user.id)
    if not user:
        #  у юзера может не быть юзернейма
        await start_user_registration(message, state)
        return

    await message.answer("Прошу введите название услуги на которую хотите записатся:\n"
                         "(или же можете выбрать через кнопку 📂 Каталог услуг)")
    await state.set_state(Requests.choose_ct)

@router.message(Requests.choose_ct)
async def get_ct(message: Message,
                 ct_sv: CatalogService,
                 state: FSMContext):
    query = message.text.strip()

    if not query:
        await message.answer("Прошу повторите заново")
        return

    bookings = await ct_sv.find_by_name(query)

    if not bookings:
        await message.answer("Включен умный поиск...")
        bookings = await ct_sv.embedding_search_by_name(query)

        if not bookings:
            logger.info(
                f"can't find catalog for name: {query}"
            )
            await message.answer("Я не нашёл такую услугу. Выберите услугу из списка", reply_markup=kb.main)
            return

    if len(bookings) > 1:
        question = phrases.ask_phrase(phrases.similar_services)

        await message.answer(
            question,
            reply_markup=kb.catalog_keyboard(bookings)
        )
        await state.set_state(Requests.many_query)
        return

    selected = bookings[0]
    await message.answer(f"Выбрана услуга: \n"
                         f"{selected.name} - {selected.price} руб / {selected.duration} мин")

    await state.update_data(user_tg_id=message.from_user.id,
                            ct_id=selected.id,
                            ct_name=selected.name)

    await state.set_state(Requests.ask_date)

@router.callback_query(Requests.many_query, F.data.startswith("catalog:"))
async def get_ct_from_many(callback: CallbackQuery,
                           state: FSMContext,
                           ct_sv: CatalogService):
    catalog_id = int(callback.data.split(":")[1])
    catalog = await ct_sv.get_ct_by_id(catalog_id)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"Выбрана услуга: \n"
                                  f"{catalog.name} - {catalog.price} руб / {catalog.duration} мин")
    await state.update_data(user_tg_id=callback.from_user.id,
                            ct_id=catalog.id,
                            ct_name=catalog.name)
    await callback.message.answer("на какую дату вы бы хотели записаться:", reply_markup=kb.get_date)
    await state.set_state(Requests.ask_date)

@router.callback_query(F.data == "today", Requests.ask_date)
async def request_today(callback: CallbackQuery,
                        state: FSMContext,
                        bk_sv: BookingService):
    date = bk_sv.today()
    await state.update_data(date=date)

    await callback.message.edit_text("Отлично 🙂, во сколько бы вы предпочли сделать запись?"
                                     "\nмы эти данные передадим администраторам и они ответят вам"
                                     "в ближайщее время")
    await callback.message.answer("Прошу введите время например (12:30 или 17 00)")
    await state.set_state(Requests.get_hour)

@router.callback_query(F.data == "another_day", Requests.ask_date)
async def request_another_day(callback: CallbackQuery,
                              state: FSMContext):

    await callback.message.edit_text("Хорошо прошу введите дату на которую хотите записатся\n"
                                     "(например 12 или 12.09 или 12.09.2026)")
    await state.set_state(Requests.get_date)

@router.message(Requests.get_date)
async def request_get_date(message: Message,
                           state: FSMContext,
                           bk_sv: BookingService):
    try:
        date_str = message.text.strip()
        date_obj = bk_sv.parse_date(date_str)
    except Exception as e:
        logger.exception(f"happened smth wrong in entering date date_str:{date_str}, e: {e}")
        await message.answer("что то пошло не так при вводе даты")
        await state.clear()
        return

    await state.update_data(date=date_obj)
    await message.answer(f"отлично вы ввели: {date_obj.strftime('%d.%m.%Y')}")
    await message.answer("Прошу введите время (например 12:30 или 17 00)")
    await state.set_state(Requests.get_hour)


@router.message(Requests.get_hour)
async def request_time(message: Message,
                       state: FSMContext):
    try:
        time_obj = message.text.strip()
    except Exception as e:
        await message.answer("что то пошло не так при вводе времени")
        logger.exception(f"happened smth wrong in entering date date_str:{time_obj}, e: {e}")
        await state.set_state(AiUserState.chatting)
        return

    await state.update_data(time=time_obj)

    await message.answer("Хорошо, Хотите ли написать примечание что бы передать администратору?:",
                         reply_markup=kb.write_comment)
    await state.set_state(Requests.get_comment)

@router.callback_query(F.data == "without_comment", Requests.get_comment)
async def request_without_comment(callback: CallbackQuery,
                                  bot: Bot,
                                  bk_sv: BookingService,
                                  ad_sv: AdminService,
                                  state: FSMContext):
    ok, text = await send_booking_request(
        state=state,
        bot=bot,
        bk_sv=bk_sv,
        ad_sv=ad_sv,
        comment="-"
    )

    data = await state.get_data()
    ct_name = data.get("name")
    ct_id = data.get("ct_id")

    await callback.message.edit_text(text)
    await callback.answer()
    await state.set_state(AiUserState.chatting)


@router.callback_query(F.data == "with_comment", Requests.get_comment)
async def request_comment(callback: CallbackQuery,
                          state: FSMContext):
    await callback.message.edit_text("Хорошо прошу напишите ниже в одном сообщении"
                                 " то что хотите передать администратору:")
    await state.set_state(Requests.create_request)

@router.message(Requests.create_request)
async def create_request(message: Message,
                         state: FSMContext,
                         bot: Bot,
                         bk_sv: BookingService,
                         ad_sv: AdminService):
    comment = message.text.strip() if message.text else "-"

    ok, text = await send_booking_request(
        state=state,
        bot=bot,
        bk_sv=bk_sv,
        ad_sv=ad_sv,
        comment=comment
    )

    await message.answer(text)
    await state.set_state(AiUserState.chatting)
'''
========================================================================================
                                     После добавления
========================================================================================
'''
@router.callback_query(F.data.startswith("bk_accept:"))
async def accept_booking(
        callback: CallbackQuery,
        bk_sv: BookingService,
        state: FSMContext):
    booking_id = int(callback.data.split(":")[1])

    booking = await bk_sv.get_booking(booking_id)

    await callback.message.edit_reply_markup(reply_markup=None)

    if not booking:
        await callback.message.answer("Заявка не найдена")
        return

    await state.update_data(booking_id=booking_id)

    await callback.message.answer("Желаете ли вы оплатить запись онлайн сейчас?", reply_markup=kb.ask_pay)

@router.callback_query(F.data == "without_pay")
async def without_pay(callback: CallbackQuery,
                      bk_sv: BookingService,
                      state: FSMContext):
    data = await state.get_data()
    booking_id = data.get("booking_id")


    if booking_id is None:
        await callback.message.answer("Ошибка: booking_id не найден", reply_markup=kb.main)
        await state.set_state(AiUserState.chatting)
        return

    try:
        await bk_sv.cancel_pay(booking_id)
        await state.set_state(AiUserState.chatting)

    except Exception as e:
        await callback.message.edit_text("что то пошло не так в хендлере")
        await callback.message.answer("Главное меню", reply_markup=kb.main)

        logger.exception(
            "failed to cancel pay, booking_id=%s, user_id=%s",
            booking_id,
            callback.from_user.id,
        )
        await state.set_state(AiUserState.chatting)
        raise

    await callback.message.edit_text("Отлично) Будем ждать вас")
    await callback.message.answer("Главное меню", reply_markup=kb.main)
    await state.set_state(AiUserState.chatting)

"""=================================================================
                               МОИ ЗАПИСИ
====================================================================
"""

@router.message(F.text == "👤Мои записи")
async def my_booking(message: Message,
                     state: FSMContext,
                     us_sv: UserService,
                     bk_sv: BookingService):
    await state.clear()
    user = await us_sv.get_by_tg_id(message.from_user.id)

    if user is None:
        #  у юзера может не быть юзернейма
        name = message.from_user.username or message.from_user.first_name
        await state.update_data(suggested_name=name)

        await message.answer(f"Давайте познакомимся 😌\n\n"
                            f"Можно обращаться к вам как {name}?",
                             reply_markup=kb.authorization)
        await state.set_state(CreateUserState.ask_name)  # продолжение в файле handler/users.py
        return

    my_bks = await bk_sv.my_bk_info(user.id)
    await state.set_state(AiUserState.chatting)
    await message.answer(my_bks)
    await message.answer("Главное меню",  reply_markup=kb.main)

# "📂 Каталог услуг"
"""=================================================================
                               Каталог услуг
====================================================================
"""

@router.message(F.text == "📂 Каталог услуг")
async def open_ct(message: Message,
                  ct_sv: CatalogService,
                  state: FSMContext,
                  us_sv: UserService):
    await state.clear()
    user = await us_sv.get_by_tg_id(message.from_user.id)

    if user is None:
        #  у юзера может не быть юзернейма
        name = message.from_user.username or message.from_user.first_name
        await state.update_data(suggested_name=name)

        await message.answer(f"Давайте познакомимся 😌\n\n"
                             f"Можно обращаться к вам как {name}?",
                             reply_markup=kb.authorization)
        await state.set_state(CreateUserState.ask_name)  # продолжение в файле handler/users.py
        return

    cts, page, total_pages = await ct_sv.page_data(page=0)

    if not cts:
        await message.answer("Каталог пока пуст.")
        logger.warning("cant get cts for 📂 Каталог услуг")
        return

    await message.answer(
        f"📂 Каталог услуг\n\nСтраница {page + 1}/{total_pages}",
        reply_markup=kb.ct_page_kb(cts, page, total_pages)
    )

    await state.set_state(Requests.choose_ct)


@router.callback_query(F.data.startswith("ct_page:"))
async def nav_btn(callback: CallbackQuery,
                  ct_sv: CatalogService,
                  state: FSMContext):
    page = int(callback.data.split(":")[1])

    cts, page, total_pages = await ct_sv.page_data(page=page)

    await callback.message.edit_text(
        f"📂 Каталог услуг\n\nСтраница {page + 1}/{total_pages}",
        reply_markup=kb.ct_page_kb(cts, page, total_pages)
    )

    await callback.answer()
    await state.set_state(Requests.choose_ct)

@router.callback_query(F.data.startswith("to_main"))
async def to_main_menu(callback: CallbackQuery,
                       state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Назад в главное меню", reply_markup=kb.main)
    await state.set_state(AiUserState.chatting)

@router.callback_query(Requests.choose_ct, F.data.startswith("catalog:"))
async def ct_select(callback: CallbackQuery,
                    ct_sv: CatalogService,
                    state: FSMContext):
    ct_id = int(callback.data.split(":")[1].strip())

    await callback.answer()

    selected = await ct_sv.get_ct_by_id(ct_id)


    if selected:
        await callback.message.edit_text(f"вы выбрали \n{selected.name} - "
                                         f"{selected.price} руб / {selected.duration} мин")
        await callback.message.answer("на какую дату вы бы хотели записаться:", reply_markup=kb.get_date)

        await state.update_data(user_tg_id=callback.from_user.id,
                                ct_id=selected.id,
                                ct_name=selected.name)
        await state.set_state(Requests.ask_date)
    else:
        logger.info(f"can't find catalog={selected.name}")
        await callback.message.edit_text("Услуга не найдена")
        await state.clear()
        await state.set_state(AiUserState.chatting)

# "❗ Удалить"
"""=================================================================
                               ❗ Удалить
====================================================================
"""

@router.message(F.text == "❗ Удалить")
async def remove_bk(message: Message,
                    state: FSMContext,
                    bk_sv: BookingService,
                    us_sv: UserService):
    await state.clear()

    user = await us_sv.get_by_tg_id(message.from_user.id)

    if user is None:
        #  у юзера может не быть юзернейма
        name = message.from_user.username or message.from_user.first_name
        await state.update_data(suggested_name=name)

        await message.answer(f"Давайте познакомимся 😌\n\n"
                             f"Можно обращаться к вам как {name}?",
                             reply_markup=kb.authorization)
        await state.set_state(CreateUserState.ask_name)  # продолжение в файле handler/users.py
        return

    try:

        bk, page, total = await bk_sv.page_data(page=0)

        if bk is None:
            await message.answer("У вас нету записей")
            await state.set_state(AiUserState.chatting)
            logger.info(
                "User has no bookings: tg_id=%s user_id=%s",
                user.tg_id,
                user.id
            )
            return

        text = await bk_sv.page_text(bk)

        await message.answer(
            f"Ваши записи\nСтраница {page + 1}/{total}"
            f"\n\n{text}\n",
            reply_markup=await kb.bk_page_kb(bk, page, total)
        )

    except Exception:
        logger.exception(
            "Failed to open booking delete page: tg_id=%s user_id=%s text=%r",
            user.tg_id,
            user.id,
            message.text
        )

        await state.set_state(AiUserState.chatting)
        await message.answer(
            "Произошла ошибка. Попробуйте позже"
        )
        raise

@router.callback_query(F.data.startswith("bk_page:"))
async def bk_nav_btn(callback: CallbackQuery,
                     bk_sv: BookingService,
                     state: FSMContext):
    page = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    try:
        bk, page, total = await bk_sv.page_data(page=page)

        if bk is None:
            await callback.message.edit_text(
                "У вас пока нет записей."
            )
            await state.set_state(AiUserState.chatting)
            await callback.answer()
            return

        text = await bk_sv.page_text(bk)

        await callback.message.edit_text(
            f"Ваши записи\nСтраница {page + 1}/{total}"
            f"\n\n{text}\n",
            reply_markup=await kb.bk_page_kb(bk, page, total)

        )

    except Exception:
        logger.exception(
            "Ошибка при удалени записей по записям: user_tg_id=%s data=%r",
            user_id,
            callback.data
        )

        await state.set_state(AiUserState.chatting)
        await callback.answer(
            "Произошла ошибка. Попробуйте позже.",
            show_alert=True
        )
        raise

@router.callback_query(F.data.startswith("remove:"))
async def ask_to_remove(callback: CallbackQuery,
                        state: FSMContext,
                        bk_sv: BookingService):
    await callback.message.edit_reply_markup(reply_markup=None)
    bk_id = int(callback.data.split(":")[1])

    try:
        bk = await bk_sv.get_booking(bk_id)

        if bk is None:
            await callback.message.answer("Такой записи не существует")
            logger.warning("can't get bk from bk_id for removing: bk_id=%s, user_tg_id=%s",
                           bk_id, callback.from_user.id)
            await state.set_state(AiUserState.chatting)
            return

        text = await bk_sv.page_text(bk)
        await callback.message.answer(
            "Вы уверены что хотите удалить это запись?"
            f"\n\n{text}",
            reply_markup=kb.confirm_remove_bk
        )

        await state.update_data(bk_id=bk_id)
        await state.set_state(RemovingBooking.ask_user)

    except Exception:

        logger.exception(
            "Ошибка при удалени записей : user_tg_id=%s data=%r",
            callback.from_user.id,
            callback.data
        )

        await state.set_state(AiUserState.chatting)
        await callback.answer(
            "Произошла ошибка. Попробуйте позже.",
            show_alert=True
        )
        raise

@router.callback_query(RemovingBooking.ask_user, F.data == "confirm_remove_bk")
async def removing_bk(callback: CallbackQuery,
                      state: FSMContext,
                      bk_sv: BookingService,
                      ad_sv: AdminService,
                      bot: Bot):
    await callback.message.edit_reply_markup(reply_markup=None)

    data = await state.get_data()
    bk_id = data.get("bk_id")

    if not isinstance(bk_id, int):
        await callback.message.answer("Ошибка: не удалось определить запись.")
        logger.warning("can't get bk_id from state_data, bk_id=%s, us_tg_id=%s",
                       bk_id, callback.from_user.id)
        return

    try:
        bk = await bk_sv.get_booking(bk_id)

        if bk is None:
            await callback.message.answer("Такой записи не существует")
            logger.warning("can't get bk from bk_id for removing: bk_id=%s, user_tg_id=%s",
                           bk_id, callback.from_user.id)
            await state.set_state(AiUserState.chatting)
            return

        await send_bk_remove(bk_id=bk_id,
                             bk_sv=bk_sv,
                             ad_sv=ad_sv,
                             bot=bot)
        await callback.message.answer("Запись успешно удалена!")

    except Exception:
        logger.exception(
            "Ошибка при удалени записей : user_tg_id=%s data=%r",
            callback.from_user.id,
            callback.data
        )

        await state.set_state(AiUserState.chatting)
        await callback.answer(
            "Произошла ошибка. Попробуйте позже.",
            show_alert=True
        )
        raise

@router.callback_query(RemovingBooking.ask_user, F.data == "cancel_remove_bk")
async def cancel_removing_bk(callback: CallbackQuery,
                      state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Удаление записи отменено", reply_markup=kb.main)
    await state.clear()
    await state.set_state(AiUserState.chatting)