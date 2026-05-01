from aiogram import Router, F
from aiogram.dispatcher.middlewares import data
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.core import keyboards as kb
from app.core.states import AdminState, CatalogSetState
from app.core.filtres import IsSuperAdmin, IsAdmin
from app.service.admin import AdminService
from app.service.catalog import CatalogService

router = Router()

@router.message(Command("admin"), IsAdmin())
async def admin_panel(message: Message):
    await message.answer("✅ Доступ открыт", reply_markup=kb.admin)


@router.message(F.text == "🪪 Добавить администратора", IsSuperAdmin())
async def get_admin_id(message: Message, state: FSMContext):
    await message.answer("введите пожалуйста ID будущего сотрудника: ")
    await message.answer("если не знаете как получить свой id "
                         "зайдите в поисковую строку и введите @getmyid_bot"
                         "\nдальше нажмите на Start или введите /start"
                         "\n\nтаким образом вы должны получить свой tg id")
    await state.set_state(AdminState.get_id)

@router.message(AdminState.get_id, IsSuperAdmin())
async def set_admin(message: Message,
                    state: FSMContext,
                    ad_sv: AdminService):
    if not message.text.isdigit():
        await message.answer("ID должно быть числом и без знаков")
        return

    tg_id = int(message.text)

    admin = await ad_sv.get_ad_by_id(tg_id)
    if not admin:
        ok = await ad_sv.set_admin(tg_id)
        if not ok:
            await message.answer("произошла ошибка! повторите попытку")
            return

        await message.answer("✅ Админ добавлен")
        await state.clear()
        return

    await message.answer("!Админ с таким id уже существует")

@router.message(F.text == "✏️ Создать услугу", IsAdmin())
async def set_catalog(message: Message, state: FSMContext):
    await message.answer("🖊️ введите название для вашей новой услуги")
    await state.set_state(CatalogSetState.get_name)

@router.message(CatalogSetState.get_name, IsAdmin())
async def get_name(message: Message, state: FSMContext):
    try:
        name_obj = message.text.strip()
    except Exception:
        await message.answer("что то пошло не так при вводе названия")
        return

    await state.update_data(name=name_obj)
    await message.answer("💸 теперь введите цену за эту услугу\n(например 500 или 100.50):")
    await state.set_state(CatalogSetState.get_price)

@router.message(CatalogSetState.get_price, IsAdmin())
async def get_price(message: Message, state: FSMContext):
    try:
        price_obj = message.text.strip()
    except Exception:
        await message.answer("что то пошло не такпри вводе цены")
        return

    await state.update_data(price=price_obj)
    await message.answer("⏳ теперь введи сколько минут длится\n(например 30 или 70):")
    await state.set_state(CatalogSetState.create)

@router.message(CatalogSetState.create, IsAdmin())
async def create_catalog(message: Message, state: FSMContext, ct_sv: CatalogService):
    duration = message.text.strip()

    data = await state.get_data()  # сохряняем все данные FSM в виде словаря
    name = data.get("name")
    price = data.get("price")

    try:
        catalog = await ct_sv.create_ct(name, price, duration)
    except Exception as e:
        await message.answer(f"❌ {e}\n\n что то пошло не так при вводе данных")
        return


    await message.answer(f"Создана новая услуга:\n\n"
                         f"id: {catalog.id}\n"
                         f"название: {catalog.name}\n"
                         f"цена: {catalog.price} руб\n"
                         f"продолжительность: {catalog.duration} мин")
    await state.clear()