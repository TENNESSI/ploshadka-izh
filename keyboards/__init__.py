from .client import (
    main_menu_keyboard,
    services_menu_keyboard,
    barbers_menu_keyboard,
    appointment_menu_keyboard,
    time_slots_keyboard,
    confirm_keyboard
)
from .admin import (
    admin_main_keyboard,
    admin_management_keyboard,
    barbers_keyboard,
    services_keyboard,
    schedule_menu_keyboard,
    appointments_keyboard,
    stats_keyboard,
    barber_actions_keyboard,
    service_actions_keyboard,
    appointment_actions_keyboard,
    days_keyboard,
    date_selection_keyboard,
    barbers_filter_keyboard,
    services_filter_keyboard,
    lock_time_keyboard,
    yes_no_inline_keyboard
)
from .builder import (
    build_time_slots_keyboard,
    build_barbers_keyboard,
    build_services_keyboard
)

__all__ = [
    # Клиентские клавиатуры
    'main_menu_keyboard',
    'services_menu_keyboard',
    'barbers_menu_keyboard',
    'appointment_menu_keyboard',
    'time_slots_keyboard',
    'confirm_keyboard',

    # Админские клавиатуры
    'admin_main_keyboard',
    'admin_management_keyboard',
    'barbers_keyboard',
    'services_keyboard',
    'schedule_menu_keyboard',
    'appointments_keyboard',
    'stats_keyboard',

    # Инлайн клавиатуры действий
    'barber_actions_keyboard',
    'service_actions_keyboard',
    'appointment_actions_keyboard',
    'yes_no_inline_keyboard',

    # Специальные клавиатуры
    'days_keyboard',
    'date_selection_keyboard',
    'barbers_filter_keyboard',
    'services_filter_keyboard',
    'lock_time_keyboard',

    # Билдеры клавиатур
    'build_time_slots_keyboard',
    'build_barbers_keyboard',
    'build_services_keyboard'
]