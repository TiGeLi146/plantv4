from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_productive_time_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton(text="Утро", callback_data="morning"),
        InlineKeyboardButton(text="День", callback_data="afternoon"),
        InlineKeyboardButton(text="Вечер", callback_data="evening"),
    ]
    keyboard.add(*buttons)
    return keyboard