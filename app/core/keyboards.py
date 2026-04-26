from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👤Мои записи")],
    [KeyboardButton(text="✏️Добавить запись")],
    [KeyboardButton(text="❗Удалить"),
    KeyboardButton(text="🎛️Другое")]],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню...")