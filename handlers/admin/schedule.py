from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from database.queries import get_work_days, update_schedule
from keyboards.admin import schedule_keyboard, days_keyboard
from states.admin_states import ScheduleStates

async def show_schedule_menu(message: types.Message):
    """Меню управления расписанием."""
    await message.answer(
        "⚙️ Управление расписанием:",
        reply_markup=schedule_keyboard()
    )

async def edit_work_days_start(message: types.Message):
    """Начало редактирования рабочих дней."""
    days = await get_work_days()  # Получаем дни из БД
    await message.answer(
        "Выберите день для редактирования:",
        reply_markup=days_keyboard(days)
    )
    await ScheduleStates.edit_days.set()

# ... другие обработчики (редактирование времени, слотов и т.д.)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(
        show_schedule_menu,
        text="📅 Расписание",
        is_admin=True
    )
    dp.register_message_handler(
        edit_work_days_start,
        text="Изменить рабочие дни",
        is_admin=True
    )
    # ... регистрация остальных обработчиков