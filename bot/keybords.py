from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_try_inline_keyboard() -> InlineKeyboardMarkup:
    # Создание объекта разметки клавиатуры
    keyboard = InlineKeyboardMarkup(row_width=1)
    # Добавление кнопки
    try_button = InlineKeyboardButton(text="Попробовать", callback_data="try")
    keyboard.add(try_button)
    return keyboard


def get_subscription_options_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton(text="1 месяц - 100 ₽", callback_data="subscription_1m"),
        InlineKeyboardButton(text="3 месяца - 300 ₽", callback_data="subscription_3m"),
        InlineKeyboardButton(text="6 месяцев - 600 ₽", callback_data="subscription_6m"),
        InlineKeyboardButton(text="12 месяцев - 1100 ₽", callback_data="subscription_12m"),
    ]
    keyboard.add(*buttons)
    return keyboard

def get_key_vpn() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton(text="Германия 🇩🇪",callback_data="germany_server"),
        InlineKeyboardButton(text="Нидерланды 🇳🇱", callback_data="amsterdam_server")
    ]
    keyboard.add(*buttons)
    return keyboard


def get_key_download() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton(text="AppStore", url='https://apps.apple.com/us/app/outline-app/id1356177741'),
        InlineKeyboardButton(text="Google Play", url='https://play.google.com/store/apps/details?id=org.outline.android.client&hl=ru&pli=1'),
        InlineKeyboardButton(text="Windows", callback_data='download_file'),
        InlineKeyboardButton(text="MacOS", url='https://apps.apple.com/us/app/outline-secure-internet-access/id1356178125?mt=12'),
        InlineKeyboardButton(text="Linux", url='https://s3.amazonaws.com/outline-releases/client/linux/stable/Outline-Client.AppImage')
    ]
    keyboard.add(*buttons)
    return keyboard
