
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_callback_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (3,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def get_url_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (3,)):
    keyboard = InlineKeyboardBuilder()

    for text, url in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, url=url))

    return keyboard.adjust(*sizes).as_markup()


def get_inlineMix_btns(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (3,)):
    keyboard = InlineKeyboardBuilder()

    for text, value in btns.items():
        if '://' in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))

    return keyboard.adjust(*sizes).as_markup()


info_btn_kb = InlineKeyboardBuilder()
info_btn_kb.add(InlineKeyboardButton(text="👨‍💻Тех.Поддержка", url="https://t.me/sample"))
info_btn_kb.add(InlineKeyboardButton(text="📕Правила", callback_data="rules"))
info_btn_kb.add(InlineKeyboardButton(text="⚙️Наши проекты", url='https://t.me/sample'))
info_btn_kb.adjust(1)


def get_main_inline_kb(support_url: str = "https://t.me/sample", has_subscription: bool = False):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="👤 Профиль", callback_data="profile"))
    keyboard.add(InlineKeyboardButton(text="➕ Добавить", callback_data="add_channel"))
    keyboard.add(InlineKeyboardButton(text="📋 Список", callback_data="list_channels"))
    if not has_subscription:
        keyboard.add(InlineKeyboardButton(text="💎 Подписка", callback_data="subscription"))
    keyboard.add(InlineKeyboardButton(text="🛠 Тех поддержка", url=support_url))
    keyboard.adjust(2, 1, 1)
    return keyboard.as_markup()