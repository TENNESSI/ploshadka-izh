from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Optional
from database.models import Barber, Service, Schedule
from datetime import datetime, timedelta


def build_time_slots_keyboard(
        available_slots: List[Schedule],
        selected_date: datetime,
        page: int = 0,
        slots_per_page: int = 6
) -> InlineKeyboardMarkup:
    """
    Строит инлайн-клавиатуру для выбора времени с пагинацией

    :param available_slots: Список доступных слотов
    :param selected_date: Выбранная дата
    :param page: Текущая страница
    :param slots_per_page: Количество слотов на странице
    :return: Объект InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=3)

    # Вычисляем слоты для текущей страницы
    start_idx = page * slots_per_page
    end_idx = start_idx + slots_per_page
    paginated_slots = available_slots[start_idx:end_idx]

    # Добавляем кнопки с временными слотами
    for slot in paginated_slots:
        keyboard.insert(
            InlineKeyboardButton(
                text=slot.time_slot.split('-')[0],
                callback_data=f"select_slot:{slot.id}"
            )
        )

    # Добавляем кнопки пагинации
    pagination_row = []
    if page > 0:
        pagination_row.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"slots_page:{page - 1}"
            )
        )

    if end_idx < len(available_slots):
        pagination_row.append(
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"slots_page:{page + 1}"
            )
        )

    if pagination_row:
        keyboard.row(*pagination_row)

    # Кнопка выбора другой даты
    keyboard.row(
        InlineKeyboardButton(
            text="📅 Выбрать другую дату",
            callback_data="change_date"
        )
    )

    return keyboard


def build_barbers_keyboard(
        barbers: List[Barber],
        selected_service_id: Optional[int] = None,
        with_back_button: bool = True
) -> InlineKeyboardMarkup:
    """
    Строит инлайн-клавиатуру для выбора барбера

    :param barbers: Список объектов Barber
    :param selected_service_id: ID выбранной услуги (для callback)
    :param with_back_button: Добавить кнопку "Назад"
    :return: Объект InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=2)

    for barber in barbers:
        callback_data = f"select_barber:{barber.id}"
        if selected_service_id:
            callback_data += f":{selected_service_id}"

        keyboard.insert(
            InlineKeyboardButton(
                text=f"🧔 {barber.name}",
                callback_data=callback_data
            )
        )

    if with_back_button:
        keyboard.row(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="back_to_services"
            )
        )

    return keyboard


def build_services_keyboard(
        services: List[Service],
        selected_barber_id: Optional[int] = None,
        with_back_button: bool = True
) -> InlineKeyboardMarkup:
    """
    Строит инлайн-клавиатуру для выбора услуги

    :param services: Список объектов Service
    :param selected_barber_id: ID выбранного барбера (для callback)
    :param with_back_button: Добавить кнопку "Назад"
    :return: Объект InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=2)

    for service in services:
        callback_data = f"select_service:{service.id}"
        if selected_barber_id:
            callback_data += f":{selected_barber_id}"

        keyboard.insert(
            InlineKeyboardButton(
                text=f"✂️ {service.name} ({service.price} руб.)",
                callback_data=callback_data
            )
        )

    if with_back_button:
        keyboard.row(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="back_to_barbers"
            )
        )

    return keyboard


def build_calendar_keyboard(
        year: int = None,
        month: int = None,
        ignore_past_dates: bool = True
) -> InlineKeyboardMarkup:
    """
    Строит клавиатуру-календарь для выбора даты

    :param year: Год (если None - текущий)
    :param month: Месяц (если None - текущий)
    :param ignore_past_dates: Игнорировать прошедшие даты
    :return: Объект InlineKeyboardMarkup
    """
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    keyboard = InlineKeyboardMarkup(row_width=7)

    # Заголовок с месяцем и годом
    month_name = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ][month - 1]

    keyboard.row(
        InlineKeyboardButton(
            text=f"{month_name} {year}",
            callback_data="ignore"
        )
    )

    # Дни недели
    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    keyboard.row(*[
        InlineKeyboardButton(
            text=day,
            callback_data="ignore"
        ) for day in week_days
    ])

    # Даты
    first_day = datetime(year, month, 1)
    last_day = datetime(
        year + 1 if month == 12 else year,
        1 if month == 12 else month + 1,
        1
    ) - timedelta(days=1)

    # Пустые кнопки для дней предыдущего месяца
    for _ in range(first_day.weekday()):
        keyboard.insert(
            InlineKeyboardButton(
                text=" ",
                callback_data="ignore"
            )
        )

    # Кнопки с датами
    current_date = datetime.now().date() if ignore_past_dates else datetime(1900, 1, 1).date()

    for day in range(1, last_day.day + 1):
        date = datetime(year, month, day).date()

        if date >= current_date:
            keyboard.insert(
                InlineKeyboardButton(
                    text=str(day),
                    callback_data=f"select_date:{date}"
                )
            )
        else:
            keyboard.insert(
                InlineKeyboardButton(
                    text=" ",
                    callback_data="ignore"
                )
            )

    # Управление календарем
    keyboard.row(
        InlineKeyboardButton(
            text="⬅️",
            callback_data=f"prev_month:{year}:{month}"
        ),
        InlineKeyboardButton(
            text="➡️",
            callback_data=f"next_month:{year}:{month}"
        )
    )

    return keyboard