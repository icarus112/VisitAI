from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton)

from database.models import Catalog

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👤Мои записи")],
    [KeyboardButton(text="✏️Добавить запись")],
    [KeyboardButton(text="❗Удалить"),
    KeyboardButton(text="🎛️Другое")]],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню...")

admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✏️ Создать услугу")],
    [KeyboardButton(text="🪪 Добавить администратора")]
])

authorization = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да, можно", callback_data="accept_name")],
    [InlineKeyboardButton(text="✏️ Ввести другое имя", callback_data="reject_name")]
])

get_date = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="☀️ Сегодня",callback_data="today")],
    [InlineKeyboardButton(text="🗓️ В другой день", callback_data="another_day")]
])

get_number = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Отправить номер", request_contact=True)],
        [KeyboardButton(text="⏭ Пропустить")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

def catalog_keyboard(catalogs):
    buttons = []

    for catalog in catalogs:
        text = f"{catalog.name} - {catalog.price} руб / {catalog.duration} мин"
        buttons.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"catalog: {catalog.id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)