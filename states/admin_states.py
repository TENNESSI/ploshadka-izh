from aiogram.filters.state import State, StatesGroup

class AdminStates(StatesGroup):
    """Базовые состояния админ-панели"""
    main_menu = State()
    stats_view = State()

class BarberManagementStates(StatesGroup):
    """Состояния управления барберами"""
    add_barber = State()
    edit_barber = State()
    delete_barber = State()

class BarberAddStates(StatesGroup):
    """Состояния для добавления барберов"""
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_photo = State()
    waiting_for_confirmation = State()
    waiting_for_deletion = State()

class ServiceManagementStates(StatesGroup):
    """Состояния управления услугами"""
    add_service = State()
    edit_service = State()
    delete_service = State()

class ScheduleManagementStates(StatesGroup):
    """Состояния управления расписанием"""
    edit_schedule = State()
    block_time = State()
    setup_template = State()