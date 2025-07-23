from aiogram import types
from aiogram.dispatcher import FSMContext
from database.queries import get_available_dates
from keyboards.client import appointment_type

async def start_appointment(message: types.Message):
    """Начало процесса записи."""
    await message.answer(
        "Как вы хотите записаться?",
        reply_markup=appointment_type()
    )
    # Устанавливаем состояние (FSM)

async def handle_time_booking(message: types.Message, state: FSMContext):
    """Обработка записи по времени."""
    dates = await get_available_dates()  # Функция из queries.py
    # Показываем даты...