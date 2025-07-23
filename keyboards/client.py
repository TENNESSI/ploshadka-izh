from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu() -> ReplyKeyboardMarkup:
    """Главное меню."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text='Записаться'), KeyboardButton(text='Мои записи')]
    ])
    return keyboard

def appointment_type() -> ReplyKeyboardMarkup:
    """Выбор типа записи."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard =[
        [KeyboardButton(text='По времени')],
        [KeyboardButton(text='По специалисту')],
        [KeyboardButton(text='По услуге')],
    ])
    return keyboard