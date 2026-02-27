from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton


menu_reply_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💎Меню"),
        ]
    ],
    resize_keyboard=True,
    persistent=True
)

main_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="1"),
        ],
        [
            KeyboardButton(text="2"),
        ],
        [
            KeyboardButton(text="3"),

            KeyboardButton(text="4"),
        ],
        [
            KeyboardButton(text="5"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите действие'
)

cancel_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отмена❌"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите действие'
)
