from aiogram.dispatcher.filters.state import State, StatesGroup

class AppointmentStates(StatesGroup):
    """Состояния процесса записи"""
    select_service = State()
    select_barber = State()
    select_date = State()
    select_time = State()
    confirm_details = State()
    payment = State()
    completed = State()