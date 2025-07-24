from datetime import datetime, timedelta, date
from typing import List, Tuple, Optional
from config import WORK_START, WORK_END, WORK_DAYS
import calendar
import locale

# Устанавливаем локаль для корректного отображения названий дней недели
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


def get_current_date() -> date:
    """Получить текущую дату (без времени)"""
    return datetime.now().date()


def get_current_datetime() -> datetime:
    """Получить текущие дату и время"""
    return datetime.now()


def format_appointment_date(dt: date) -> str:
    """
    Форматировать дату для отображения
    Пример: "12 мая, пятница"
    """
    return dt.strftime("%d %B, %A").lower()


def format_short_date(dt: date) -> str:
    """Короткий формат даты (12.05.2023)"""
    return dt.strftime("%d.%m.%Y")


def format_time_slot(start_time: str, end_time: str) -> str:
    """
    Форматировать временной слот
    Пример: "10:00 - 11:30"
    """
    return f"{start_time} - {end_time}"


def parse_appointment_date(date_str: str) -> Optional[date]:
    """
    Парсить дату из строки формата 'DD.MM.YYYY'
    Возвращает date или None при ошибке
    """
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        return None


def generate_time_slots(
        duration: int = 30,
        work_start: int = WORK_START,
        work_end: int = WORK_END
) -> List[Tuple[str, str]]:
    """
    Сгенерировать временные слоты на день

    Args:
        duration: продолжительность слота в минутах
        work_start: час начала работы
        work_end: час окончания работы

    Returns:
        Список кортежей (начало, конец) в формате "HH:MM"
    """
    slots = []
    current_time = datetime.strptime(f"{work_start}:00", "%H:%M")
    end_time = datetime.strptime(f"{work_end}:00", "%H:%M")

    while current_time + timedelta(minutes=duration) <= end_time:
        slot_end = current_time + timedelta(minutes=duration)
        slots.append(
            (current_time.strftime("%H:%M"), slot_end.strftime("%H:%M"))
        )
        current_time = slot_end

    return slots


def get_week_dates(start_date: date = None) -> List[date]:
    """
    Получить даты на неделю вперед от указанной даты (по умолчанию текущая)
    """
    start = start_date or get_current_date()
    return [start + timedelta(days=i) for i in range(7)]


def is_work_day(check_date: date) -> bool:
    """
    Проверить, является ли дата рабочим днем
    """
    return check_date.weekday() in WORK_DAYS


def get_next_work_day(after_date: date = None) -> date:
    """
    Получить следующий рабочий день
    """
    current = after_date or get_current_date()
    while True:
        current += timedelta(days=1)
        if is_work_day(current):
            return current


def get_month_range(year: int = None, month: int = None) -> Tuple[date, date]:
    """
    Получить первый и последний день месяца
    """
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    first_day = date(year, month, 1)
    last_day = date(
        year + 1 if month == 12 else year,
        1 if month == 12 else month + 1,
        1
    ) - timedelta(days=1)

    return first_day, last_day


def validate_future_date(input_date: date) -> bool:
    """
    Проверить что дата не в прошлом
    """
    return input_date >= get_current_date()


def get_available_dates(
        days_ahead: int = 30,
        only_work_days: bool = True
) -> List[date]:
    """
    Получить список доступных дат для записи

    Args:
        days_ahead: на сколько дней вперед
        only_work_days: только рабочие дни

    Returns:
        Список доступных дат
    """
    current = get_current_date()
    dates = []

    for i in range(days_ahead):
        check_date = current + timedelta(days=i)
        if not only_work_days or is_work_day(check_date):
            dates.append(check_date)

    return dates


def get_human_readable_schedule(schedule: dict) -> str:
    """
    Преобразовать расписание в читаемый формат

    Args:
        schedule: словарь с расписанием {день: [временные слоты]}

    Returns:
        Отформатированная строка с расписанием
    """
    result = []
    for day, slots in schedule.items():
        day_name = day.strftime("%A").capitalize()
        slots_str = ", ".join(slots)
        result.append(f"{day_name}: {slots_str}")

    return "\n".join(result)


def calculate_end_time(start_time: str, duration: int) -> str:
    """
    Рассчитать время окончания по времени начала и продолжительности

    Args:
        start_time: время начала "HH:MM"
        duration: продолжительность в минутах

    Returns:
        Время окончания "HH:MM"
    """
    start = datetime.strptime(start_time, "%H:%M")
    end = start + timedelta(minutes=duration)
    return end.strftime("%H:%M")