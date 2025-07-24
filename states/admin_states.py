from aiogram.dispatcher.filters.state import State, StatesGroup

class AdminStates(StatesGroup):
    """Базовые состояния админ-панели"""
    main_menu = State()
    stats_view = State()

class BarberManagementStates(StatesGroup):
    """Состояния управления барберами"""
    add_barber = State()
    edit_barber = State()
    delete_barber = State()

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