from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from database.queries import get_db_session, get_active_barbers, get_all_services
from datetime import datetime, timedelta


# ====================== ГЛАВНЫЕ МЕНЮ ======================

def admin_main_keyboard():
    """Главное меню администратора"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Управление"), KeyboardButton("Статистика")],
            [KeyboardButton("Выйти из админки")]
        ],
        resize_keyboard=True
    )


def admin_management_keyboard():
    """Меню управления компонентами"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Барберы"), KeyboardButton("Услуги")],
            [KeyboardButton("Расписание"), KeyboardButton("Записи")],
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True
    )


# ====================== БАРБЕРЫ ======================

def barbers_keyboard():
    """Меню управления барберами"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Добавить барбера"), KeyboardButton("Удалить барбера")],
            [KeyboardButton("Список барберов")],
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True
    )


def barbers_for_schedule_keyboard():
    """Клавиатура выбора барберов для расписания"""
    with get_db_session() as session:
        barbers = get_active_barbers(session)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for barber in barbers:
        keyboard.add(KeyboardButton(f"{barber.name} [{barber.id}]"))
    keyboard.add(KeyboardButton("Отмена"))
    return keyboard


def barber_actions_keyboard(barber_id: int):
    """Инлайн-кнопки для действий с барбером"""
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("✏️ Изменить", callback_data=f"edit_barber:{barber_id}"),
        InlineKeyboardButton("❌ Удалить", callback_data=f"delete_barber:{barber_id}")
    )


# ====================== УСЛУГИ ======================

def services_keyboard():
    """Меню управления услугами"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Добавить услугу"), KeyboardButton("Удалить услугу")],
            [KeyboardButton("Список услуг")],
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True
    )


def service_actions_keyboard(service_id: int):
    """Инлайн-кнопки для действий с услугой"""
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("✏️ Изменить", callback_data=f"edit_service:{service_id}"),
        InlineKeyboardButton("❌ Удалить", callback_data=f"delete_service:{service_id}")
    )


# ====================== РАСПИСАНИЕ ======================

def schedule_menu_keyboard():
    """Меню управления расписанием"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Настроить расписание"), KeyboardButton("Просмотр записей")],
            [KeyboardButton("Заблокировать время"), KeyboardButton("Шаблоны")],
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True
    )


def days_keyboard(days: list):
    """Клавиатура выбора дней"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for day in days:
        keyboard.add(KeyboardButton(day.strftime("%a, %d.%m")))  # "Пн, 15.01"
    keyboard.add(KeyboardButton("Другой день"))
    keyboard.add(KeyboardButton("Отмена"))
    return keyboard


def time_slots_keyboard(slots: list):
    """Инлайн-клавиатура выбора временных слотов"""
    keyboard = InlineKeyboardMarkup(row_width=3)
    for slot in slots:
        keyboard.insert(InlineKeyboardButton(
            text=slot,
            callback_data=f"slot:{slot}"
        ))
    keyboard.add(InlineKeyboardButton(
        text="✅ Подтвердить выбор",
        callback_data="confirm_slots"
    ))
    return keyboard


def lock_time_keyboard():
    """Клавиатура для блокировки времени"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Заблокировать день"), KeyboardButton("Заблокировать слот")],
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True
    )


# ====================== ЗАПИСИ ======================

def appointments_keyboard():
    """Меню управления записями"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Сегодня"), KeyboardButton("Завтра")],
            [KeyboardButton("Неделя"), KeyboardButton("Фильтр записей")],
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True
    )


def barbers_filter_keyboard():
    """Клавиатура фильтрации по барберам"""
    with get_db_session() as session:
        barbers = get_active_barbers(session)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for barber in barbers:
        keyboard.add(KeyboardButton(f"{barber.name} [{barber.id}]"))
    keyboard.add(KeyboardButton("Все барберы"))
    keyboard.add(KeyboardButton("Отмена"))
    return keyboard


def services_filter_keyboard():
    """Клавиатура фильтрации по услугам"""
    with get_db_session() as session:
        services = get_all_services(session)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for service in services:
        keyboard.add(KeyboardButton(f"{service.name} [{service.id}]"))
    keyboard.add(KeyboardButton("Все услуги"))
    keyboard.add(KeyboardButton("Отмена"))
    return keyboard


def date_selection_keyboard(days_ahead: int = 7):
    """Клавиатура выбора даты"""
    dates = [datetime.now() + timedelta(days=i) for i in range(1, days_ahead + 1)]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for date in dates:
        keyboard.add(KeyboardButton(date.strftime("%d.%m.%Y")))
    keyboard.add(KeyboardButton("Отмена"))
    return keyboard


def appointment_actions_keyboard(appointment_id: int):
    """Инлайн-кнопки для действий с записью"""
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_app:{appointment_id}"),
        InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_app:{appointment_id}"),
        InlineKeyboardButton("✏️ Изменить", callback_data=f"edit_app:{appointment_id}")
    )


# ====================== СТАТИСТИКА ======================

def stats_keyboard():
    """Меню статистики"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Текущий месяц"), KeyboardButton("Прошлый месяц")],
            [KeyboardButton("Произвольный период")],
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True
    )


# ====================== ОБЩИЕ КЛАВИАТУРЫ ======================

def confirm_keyboard():
    """Клавиатура подтверждения"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Да"), KeyboardButton("Нет")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def cancel_keyboard():
    """Клавиатура отмены"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def back_keyboard():
    """Кнопка назад"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("Назад")]],
        resize_keyboard=True
    )


def yes_no_inline_keyboard(action: str, id: int):
    """Инлайн-клавиатура Да/Нет"""
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton("Да", callback_data=f"{action}_yes:{id}"),
        InlineKeyboardButton("Нет", callback_data=f"{action}_no:{id}")
    )