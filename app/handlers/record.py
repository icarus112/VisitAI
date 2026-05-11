import datetime

from aiogram import Router, F, Bot
from aiogram.client import bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.core import keyboards as kb
from app.core.states import CreateUserState, Requests
from app.service.admin import AdminService
from app.service.booking import BookingService
from app.service.catalog import CatalogService
from app.service.user import UserService

router = Router()
#проверить ввод даты
#проверить без комента
'''
========================================================================================
                                     ДОБАВИТЬ ЗАПИСЬ
========================================================================================
'''

@router.message(F.text == "✏️Добавить запись")
async def add_record(message: Message, state: FSMContext,
                     us_sv: UserService, ct_sv: CatalogService):

    await state.clear()

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

    await state.set_state(Requests.choose_ct)
    await show_catalogs(message, ct_sv)

async def show_catalogs(message: Message, ct_sv: CatalogService):
    catalogs = await ct_sv.get_all()

    await message.answer(
        "😌 Давайте выберем услугу",
        reply_markup=kb.catalog_keyboard(catalogs)
    )

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

        await state.update_data(user_tg_id=callback.from_user.id)
        await state.update_data(ct_id=selected.id)
        await state.set_state(Requests.ask_date)
    else:
        await callback.message.edit_text("Услуга не найдена")
        await state.clear()

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
        date_obj = message.text.strip()
        date_obj = bk_sv.parse_date(date_obj)
    except Exception as e:
        await message.answer("что то пошло не так при вводе даты")
        print(e)
        await state.clear()
        return

    await state.update_data(date=date_obj)
    await message.answer(f"отлично вы ввели: {date_obj.strftime('%d.%m.%Y')}")
    await message.answer("Прошу введите время например (12:30 или 17 00)")
    await state.set_state(Requests.get_hour)


@router.message(Requests.get_hour)
async def request_time(message: Message,
                       state: FSMContext):
    try:
        time_obj = message.text.strip()
    except Exception:
        await message.answer("что то пошло не так при вводе времени")
        await state.clear()
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

    await callback.message.edit_text(text)
    await callback.answer()
    await state.clear()


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
    await state.clear()

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
        print(e)
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

    return True, "Заявка отправлена администратору"
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
        return

    try:
        await bk_sv.cancel_pay(booking_id)
    except Exception as e:
        await callback.message.edit_text("что то пошло не так в хендлере")
        await callback.message.answer("Главное меню", reply_markup=kb.main)
        print(e)
        return

    await callback.message.edit_text("Отлично) Будем ждать вас")
    await callback.message.answer("Главное меню", reply_markup=kb.main)




