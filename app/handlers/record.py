from aiogram import Router, F, Bot
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

'''
========================================================================================
                                     ДОБАВИТЬ ЗАПИСЬ
========================================================================================
'''

@router.message(F.text == "✏️Добавить запись")
async def add_record(message: Message, state: FSMContext,
                     us_sv: UserService, ct_sv: CatalogService):

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

    await show_catalogs(message, ct_sv)

async def show_catalogs(message: Message, ct_sv: CatalogService):
    catalogs = await ct_sv.get_all()

    await message.answer(
        "😌 Давайте выберем услугу",
        reply_markup=kb.catalog_keyboard(catalogs)
    )

@router.callback_query(F.data.startswith("catalog:"))
async def ct_select(callback: CallbackQuery,
                    ct_sv: CatalogService,
                    state: FSMContext):
    ct_id = int(callback.data.split(":")[1].strip())
    cts = await ct_sv.get_all()

    await callback.answer()

    selected = await ct_sv.get_ct_by_id(ct_id)


    if selected:
        await callback.message.edit_text(f"вы выбрали \n{selected.name} - "
                                         f"{selected.price} руб / {selected.duration} мин")
        await callback.message.answer("на какую дату вы бы хотели записаться:", reply_markup=kb.get_date)

        await state.update_data(user_tg_id=callback.from_user.id)
        await state.update_data(ct_id=selected.id)
        await state.set_state(Requests.get_date)
    else:
        await callback.message.edit_text("Услуга не найдена")

@router.callback_query(F.data == "today", Requests.get_date)
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

@router.message(Requests.get_hour)
async def request_time(message: Message,
                       state: FSMContext):
    try:
        time_obj = message.text.strip()
    except Exception:
        await message.answer("что то пошло не так при вводе времени")
        return

    await state.update_data(time=time_obj)

    await message.answer("Хорошо, Хотите ли написать примечание что бы передать администратору?:",
                         reply_markup=kb.write_comment)
    await state.set_state(Requests.get_comment)


@router.callback_query(F.data == "with_comment", Requests.get_comment)
async def request_comment(callback: CallbackQuery,
                          state: FSMContext):
    await callback.message.answer("Хорошо прошу напишите ниже в одном сообщении"
                                 " то что хотите передать администратору:")
    await state.set_state(Requests.create_request)

@router.message(Requests.create_request)
async def create_request(message: Message,
                         state: FSMContext,
                         bot: Bot,
                         bk_sv: BookingService,
                         ad_sv: AdminService):
    comment = message.text.strip() if message.text else ""

    data = await state.get_data()
    user_tg_id = data.get("user_tg_id")
    ct_id = data.get("ct_id")
    time_str = data.get("time")
    date_str = data.get("date")

    if not user_tg_id or not ct_id or not time_str or not date_str:
        await message.answer("Не хватает данных для создания заявки")
        return

    try:

        result = await bk_sv.create_booking(
            tg_id=user_tg_id,
            ct_id=ct_id,
            date_str=date_str,
            time_str=time_str,
            comment=comment
        )

    except Exception as e:
        await message.answer("Ошибка при создании заявки")
        print(e)
        return

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
        await message.answer("Ошибка при получении выборки администраторов")
        print(e)
        return

    for admin in admins:
        await bot.send_message(
            chat_id = admin.tg_id,
            text=text,
            reply_markup=kb.admin_booking(booking.id)
        )

    await message.answer("✅ Заявка создана и отправлена администратору")
    await state.clear()




















