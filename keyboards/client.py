from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from datetime import datetime, timedelta
from database.queries import get_db_session, get_active_barbers, get_all_services


# ====================== ОСНОВНЫЕ МЕНЮ ======================

def main_menu_keyboard():
    """Главное меню клиента"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("✂️ Услуги"), KeyboardButton("🧔 Барберы")],
            [KeyboardButton("📅 Мои записи")],
            [KeyboardButton("📞 Контакты"), KeyboardButton("ℹ️ О нас")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню..."
    )


def back_to_main_keyboard():
    """Клавиатура с кнопкой возврата в главное меню"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("🏠 Главное меню")]],
        resize_keyboard=True
    )


# ====================== МЕНЮ УСЛУГ ======================

def services_menu_keyboard():
    """Меню выбора услуг"""
    with get_db_session() as session:
        services = get_all_services(session)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    # Добавляем услуги по 2 в ряд
    for i in range(0, len(services), 2):
        row = services[i:i + 2]
        keyboard.row(*[KeyboardButton(f"✂️ {s.name}") for s in row])

    keyboard.add(KeyboardButton("🏠 Главное меню"))
    return keyboard


def service_details_keyboard(service_id: int):
    """Инлайн-кнопки для выбранной услуги"""
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("📅 Записаться", callback_data=f"book_service:{service_id}"),
        InlineKeyboardButton("ℹ️ Подробнее", callback_data=f"service_info:{service_id}")
    )


# ====================== МЕНЮ БАРБЕРОВ ======================

def barbers_menu_keyboard():
    """Меню выбора барберов"""
    with get_db_session() as session:
        barbers = get_active_barbers(session)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    # Добавляем барберов по 2 в ряд
    for i in range(0, len(barbers), 2):
        row = barbers[i:i + 2]
        keyboard.row(*[KeyboardButton(f"🧔 {b.name}") for b in row])

    keyboard.add(KeyboardButton("🏠 Главное меню"))
    return keyboard


def barber_details_keyboard(barber_id: int):
    """Инлайн-кнопки для выбранного барбера"""
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("📅 Записаться", callback_data=f"book_barber:{barber_id}"),
        InlineKeyboardButton("📷 Фото работ", callback_data=f"barber_portfolio:{barber_id}")
    )


# ====================== ЗАПИСЬ НА УСЛУГУ ======================

def appointment_menu_keyboard():
    """Меню записи на услугу"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("📅 По дате"), KeyboardButton("🧔 По барберу")],
            [KeyboardButton("✂️ По услуге")],
            [KeyboardButton("🏠 Главное меню")]
        ],
        resize_keyboard=True
    )


def time_slots_keyboard(slots: list):
    """Инлайн-клавиатура выбора времени"""
    keyboard = InlineKeyboardMarkup(row_width=3)

    for slot in slots:
        keyboard.insert(InlineKeyboardButton(
            text=slot,
            callback_data=f"select_time:{slot}"
        ))

    keyboard.add(InlineKeyboardButton(
        text="🔄 Другая дата",
        callback_data="change_date"
    ))
    return keyboard


def confirm_appointment_keyboard():
    """Клавиатура подтверждения записи"""
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_appointment"),
        InlineKeyboardButton("❌ Отменить", callback_data="cancel_appointment")
    )


# ====================== МОИ ЗАПИСИ ======================

def my_appointments_keyboard(appointments: list):
    """Клавиатура для списка записей пользователя"""
    keyboard = InlineKeyboardMarkup()

    for app in appointments:
        keyboard.add(InlineKeyboardButton(
            text=f"{app.date} {app.time_slot} - {app.service.name}",
            callback_data=f"appointment_{app.id}"
        ))

    return keyboard


def appointment_actions_keyboard(appointment_id: int):
    """Кнопки действий с конкретной записью"""
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("✏️ Изменить", callback_data=f"edit_{appointment_id}"),
        InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_{appointment_id}")
    )


# ====================== ОБЩИЕ КЛАВИАТУРЫ ======================

def confirm_keyboard():
    """Клавиатура подтверждения/отмены"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("✅ Да"), KeyboardButton("❌ Нет")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def cancel_keyboard():
    """Клавиатура отмены действия"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("🚫 Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )