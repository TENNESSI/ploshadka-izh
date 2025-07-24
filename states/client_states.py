from aiogram.dispatcher.filters.state import State, StatesGroup

class ClientRegistrationStates(StatesGroup):
    """Состояния регистрации клиента"""
    enter_name = State()
    enter_phone = State()
    confirm_data = State()

class ServiceSelectionStates(StatesGroup):
    """Состояния выбора услуги"""
    main_menu = State()
    select_category = State()
    select_service = State()

class BarberSelectionStates(StatesGroup):
    """Состояния выбора барбера"""
    select_from_all = State()
    select_by_service = State()

class DateTimeSelectionStates(StatesGroup):
    """Состояния выбора даты и времени"""
    select_date = State()
    select_time = State()
    confirm_datetime = State()