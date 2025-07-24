from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime, timedelta
from database.queries import (
    get_db_session,
    get_active_barbers,
    get_available_slots,
    add_schedule_slot,
    generate_time_slots
)
from keyboards.admin import (
    schedule_menu_keyboard,
    barbers_for_schedule_keyboard,
    days_keyboard,
    cancel_keyboard,
    confirm_keyboard
)
from utils.date_utils import get_next_dates


class ScheduleStates(StatesGroup):
    """FSM состояния для управления расписанием"""
    select_barber = State()
    select_day = State()
    select_slots = State()
    confirm_slots = State()
    custom_day = State()


# Главное меню расписания
async def show_schedule_menu(message: types.Message):
    """Показать меню управления расписанием"""
    await message.answer(
        "📅 Управление расписанием:",
        reply_markup=schedule_menu_keyboard()
    )


# Начало настройки расписания
async def setup_schedule_start(message: types.Message):
    """Начало настройки расписания"""
    with get_db_session() as session:
        barbers = get_active_barbers(session)

    if not barbers:
        await message.answer("Нет активных барберов для настройки расписания")
        return

    await message.answer(
        "Выберите барбера:",
        reply_markup=barbers_for_schedule_keyboard(barbers)
    )
    await ScheduleStates.select_barber.set()


# Выбор дня для настройки
async def select_day_for_schedule(message: types.Message, state: FSMContext):
    """Обработка выбора барбера и переход к выбору дня"""
    if message.text == "Отмена":
        await message.answer("Отменено", reply_markup=schedule_menu_keyboard())
        await state.finish()
        return

    async with state.proxy() as data:
        # Сохраняем имя барбера (для удобства)
        data['barber_name'] = message.text
        # Получаем ID барбера из текста кнопки (формат: "Имя [ID]")
        try:
            barber_id = int(message.text.split('[')[-1].replace(']', ''))
            data['barber_id'] = barber_id
        except:
            await message.answer("Ошибка выбора барбера")
            await state.finish()
            return

    await message.answer(
        "Выберите день для настройки:",
        reply_markup=days_keyboard(get_next_dates(7))  # Следующие 7 дней
    )
    await ScheduleStates.select_day.set()


# Обработка выбранного дня
async def process_selected_day(message: types.Message, state: FSMContext):
    """Обработка выбранного дня и генерация слотов"""
    if message.text == "Другой день":
        await message.answer(
            "Введите дату в формате ДД.ММ.ГГГГ (например, 15.01.2023):",
            reply_markup=cancel_keyboard()
        )
        await ScheduleStates.custom_day.set()
        return

    if message.text == "Отмена":
        await message.answer("Отменено", reply_markup=schedule_menu_keyboard())
        await state.finish()
        return

    async with state.proxy() as data:
        try:
            # Парсим дату из текста (формат: "Пн, 15.01")
            day_str = message.text.split(', ')[1]
            day = datetime.strptime(day_str, "%d.%m").date()
            current_year = datetime.now().year
            data['date'] = day.replace(year=current_year).strftime("%Y-%m-%d")
        except:
            await message.answer("Неверный формат даты")
            return

    # Генерируем стандартные слоты
    slots = generate_time_slots()

    await message.answer(
        "Выберите временные слоты для работы:",
        reply_markup=create_slots_keyboard(slots)
    )
    await ScheduleStates.select_slots.set()


# Обработка кастомной даты
async def process_custom_day(message: types.Message, state: FSMContext):
    """Обработка введенной вручную даты"""
    try:
        date = datetime.strptime(message.text, "%d.%m.%Y").date()
        async with state.proxy() as data:
            data['date'] = date.strftime("%Y-%m-%d")

        slots = generate_time_slots()

        await message.answer(
            "Выберите временные слоты для работы:",
            reply_markup=create_slots_keyboard(slots)
        )
        await ScheduleStates.select_slots.set()
    except ValueError:
        await message.answer("Неверный формат даты. Попробуйте снова:")
        return


# Подтверждение выбранных слотов
async def confirm_selected_slots(callback: types.CallbackQuery, state: FSMContext):
    """Подтверждение выбранных временных слотов"""
    selected_slots = callback.data.split(':')[1].split(',')

    async with state.proxy() as data:
        data['selected_slots'] = selected_slots
        barber_name = data['barber_name']
        date = datetime.strptime(data['date'], "%Y-%m-%d").strftime("%d.%m.%Y")

    slots_text = "\n".join(f"• {slot}" for slot in selected_slots)

    await callback.message.edit_text(
        f"Подтвердите расписание для {barber_name} на {date}:\n\n"
        f"{slots_text}\n\n"
        f"Все верно?",
        reply_markup=confirm_keyboard()
    )
    await ScheduleStates.confirm_slots.set()


# Сохранение расписания
async def save_schedule(message: types.Message, state: FSMContext):
    """Сохранение расписания в базу данных"""
    if message.text.lower() != 'да':
        await message.answer("Настройка расписания отменена",
                             reply_markup=schedule_menu_keyboard())
        await state.finish()
        return

    async with state.proxy() as data:
        barber_id = data['barber_id']
        date = data['date']
        slots = data['selected_slots']

    with get_db_session() as session:
        for slot in slots:
            add_schedule_slot(
                session=session,
                barber_id=barber_id,
                date=date,
                time_slot=slot
            )

    await message.answer(
        "Расписание успешно сохранено!",
        reply_markup=schedule_menu_keyboard()
    )
    await state.finish()


# Вспомогательные функции
def create_slots_keyboard(slots: list) -> types.InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру для выбора слотов"""
    keyboard = types.InlineKeyboardMarkup(row_width=3)

    for slot in slots:
        keyboard.insert(
            types.InlineKeyboardButton(
                text=slot,
                callback_data=f"slot:{slot}"
            )
        )

    keyboard.add(
        types.InlineKeyboardButton(
            text="✅ Подтвердить выбор",
            callback_data="confirm_slots"
        )
    )

    return keyboard


# Регистрация обработчиков
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(
        show_schedule_menu,
        text="Расписание",
        is_admin=True
    )

    dp.register_message_handler(
        setup_schedule_start,
        text="Настроить расписание",
        is_admin=True
    )

    dp.register_message_handler(
        select_day_for_schedule,
        state=ScheduleStates.select_barber
    )

    dp.register_message_handler(
        process_selected_day,
        state=ScheduleStates.select_day
    )

    dp.register_message_handler(
        process_custom_day,
        state=ScheduleStates.custom_day
    )

    dp.register_callback_query_handler(
        confirm_selected_slots,
        lambda c: c.data.startswith("confirm_slots") or "slot:" in c.data,
        state=ScheduleStates.select_slots
    )

    dp.register_message_handler(
        save_schedule,
        state=ScheduleStates.confirm_slots
    )