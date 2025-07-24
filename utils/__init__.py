from .date_utils import (
    get_current_date,
    format_appointment_date,
    parse_appointment_date,
    generate_time_slots,
    get_week_dates,
    is_work_day,
)
from .notifications import (
    send_welcome_message,
    send_reminder,
    notify_admins,
    send_appointment_confirmation
)

# Экспорт всех утилит для удобного импорта
__all__ = [
    # date_utils
    'get_current_date',
    'format_appointment_date',
    'parse_appointment_date',
    'generate_time_slots',
    'get_week_dates',
    'is_work_day',

    # notifications
    'send_welcome_message',
    'send_reminder',
    'notify_admins',
    'send_appointment_confirmation',
]


# Альтернативный вариант экспорта по категориям
class Utils:
    """Контейнер для всех утилит проекта"""

    class date:
        get_current = get_current_date
        format = format_appointment_date
        parse = parse_appointment_date
        generate_slots = generate_time_slots
        get_week = get_week_dates
        is_workday = is_work_day

    class notify:
        welcome = send_welcome_message
        reminder = send_reminder
        admins = notify_admins
        confirm = send_appointment_confirmation