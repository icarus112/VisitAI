from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton)

from database.models import Catalog

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👤Мои записи")],
    [KeyboardButton(text="✏️Добавить запись")],
    [KeyboardButton(text="❗ Удалить запись")],
    [KeyboardButton(text="🪪 Связаться с администратором")]],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню...")

admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✏️ Создать услугу"),
     KeyboardButton(text="⚙️ Изменить услугу")],
    [KeyboardButton(text="❓ Создать FAQ"),
     KeyboardButton(text="️️⚙️ Изменить FAQ")],
    [KeyboardButton(text="🪪 Сотрудники")],
])

super_panel =ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🪪 Добавить администратора"),
     KeyboardButton(text="Удалить администратора")],
    [KeyboardButton(text="📃 Список работников")]
])

authorization = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да, можно", callback_data="accept_name")],
    [InlineKeyboardButton(text="✏️ Ввести другое имя", callback_data="reject_name")]
])

get_date = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="☀️ Сегодня",callback_data="today")],
    [InlineKeyboardButton(text="🗓️ В другой день", callback_data="another_day")]
])

write_comment = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да, написать", callback_data="with_comment")],
    [InlineKeyboardButton(text="❌ Без комментариев", callback_data="without_comment")]
])

ask_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да, оплатить сейчас", callback_data="accept_pay")],
    [InlineKeyboardButton(text="❌ Оплатить на месте", callback_data="without_pay")]
])

get_number = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Отправить номер", request_contact=True)],
        [KeyboardButton(text="⏭ Пропустить")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

confirm_ai_booking = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_ai_booking"),
    InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_ai_booking")
    ]
])

confirm_ai_create_ct = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_ai_create_ct"),
     InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_ai_create_ct")
    ]
])

"""
=============================================================
=============================================================
"""

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

def admins_keyboard(admins):
    buttons = []
    for admin in admins:
        text = f"{admin.name}\n{admin.tg_id}"
        buttons.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"admin: {admin.id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_booking(booking_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять",
                    callback_data=f"bk_accept:{booking_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Написать клиенту",
                    callback_data=f"bk_reject:{booking_id}"
                )
            ]
        ]
    )

def ct_page_kb(cts: list[Catalog], page: int, total_pages: int):
    buttons = []

    for ct in cts:
        buttons.append([
            InlineKeyboardButton(
                text=f" {ct.name} -"
                     f" {ct.price} руб / {ct.duration} мин",
                callback_data=f"catalog: {ct.id}"
            )
        ])

    nav_buttons = []

    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"ct_page:{page - 1}"
            )
        )

    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"ct_page:{page + 1}"
            )
        )

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append(
        [InlineKeyboardButton(
            text="☰ Главное меню",
            callback_data="to_main"
        )]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
