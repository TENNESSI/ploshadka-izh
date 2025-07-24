from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.queries import (
    get_db_session,
    get_appointments_by_date,
    get_appointment_by_id,
    cancel_appointment,
    confirm_appointment
)
from database.models import Appointment, Barber, Service
from keyboards.admin import (
    appointments_keyboard,
    appointment_actions_keyboard,
    confirm_keyboard,
    cancel_keyboard
)
from utils.date_utils import (
    get_current_date,
    format_appointment_date
)


class AppointmentStates(StatesGroup):
    """FSM состояния для управления записями"""
    select_date = State()
    cancel_confirmation = State()


async def show_appointments_menu(message: types.Message):
    """Показать меню записей"""
    await message.answer(
        "📋 Управление записями:",
        reply_markup=appointments_keyboard()
    )


async def show_week_appointments(message: types.Message):
    """Показать записи на неделю вперед"""
    with get_db_session() as session:
        start_date = get_current_date()
        end_date = start_date + timedelta(days=7)

        appointments = session.query(Appointment).filter(
            Appointment.date.between(start_date, end_date)
        ).order_by(
            Appointment.date,
            Appointment.time_slot
        ).all()

    if not appointments:
        await message.answer(
            "На ближайшую неделю записей нет",
            reply_markup=appointments_keyboard()
        )
        return

    # Группируем записи по дням
    appointments_by_day = {}
    for app in appointments:
        day = app.date.strftime("%d.%m.%Y")
        if day not in appointments_by_day:
            appointments_by_day[day] = []
        appointments_by_day[day].append(app)

    # Формируем сообщение
    response = ["📅 Записи на ближайшую неделю:\n"]
    for day, day_appointments in appointments_by_day.items():
        response.append(f"\n📌 {day}:")
        for app in day_appointments:
            status_icon = "✅" if app.status == 'confirmed' else "🕒" if app.status == 'booked' else "❌"
            response.append(
                f"{status_icon} {app.time_slot} - {app.barber.name}\n"
                f"Услуга: {app.service.name} | ID: {app.id}"
            )

    await message.answer(
        "\n".join(response),
        reply_markup=appointments_keyboard()
    )


async def show_appointments_by_date(message: types.Message):
    """Обработка выбора даты для просмотра записей"""
    date_map = {
        "Сегодня": get_current_date(),
        "Завтра": get_current_date() + timedelta(days=1),
        "Неделя": None
    }

    if message.text not in date_map:
        await message.answer("Неизвестная команда")
        return

    selected_date = date_map[message.text]

    if message.text == "Неделя":
        await show_week_appointments(message)
        return

    await view_appointments_on_date(message, selected_date)


async def view_appointments_on_date(message: types.Message, date: datetime.date):
    """Показать записи на конкретную дату"""
    with get_db_session() as session:
        appointments = get_appointments_by_date(session, date)

    if not appointments:
        await message.answer(
            f"На {format_appointment_date(date)} записей нет",
            reply_markup=appointments_keyboard()
        )
        return

    response = [f"📅 Записи на {format_appointment_date(date)}:\n"]
    for app in appointments:
        status_icon = "✅" if app.status == 'confirmed' else "🕒" if app.status == 'booked' else "❌"
        response.append(
            f"\n{status_icon} {app.time_slot} - {app.barber.name}\n"
            f"Услуга: {app.service.name} ({app.service.price} руб.)\n"
            f"ID записи: {app.id}"
        )

    await message.answer(
        "\n".join(response),
        reply_markup=appointment_actions_keyboard(appointments[0].id)
    )


async def handle_appointment_action(callback: types.CallbackQuery, state: FSMContext):
    """Обработка действий с записью"""
    action, appointment_id = callback.data.split(':')
    appointment_id = int(appointment_id)

    with get_db_session() as session:
        appointment = get_appointment_by_id(session, appointment_id)
        if not appointment:
            await callback.answer("Запись не найдена!")
            return

        if action == "confirm_app":
            confirm_appointment(session, appointment_id)
            await callback.message.edit_text(
                f"✅ Запись ID {appointment_id} подтверждена\n"
                f"{format_appointment_details(appointment)}",
                reply_markup=appointment_actions_keyboard(appointment_id)
            )
            await callback.answer("Запись подтверждена!")

        elif action == "cancel_app":
            async with state.proxy() as data:
                data['appointment_id'] = appointment_id
            await callback.message.answer(
                f"Вы уверены, что хотите отменить запись ID {appointment_id}?",
                reply_markup=confirm_keyboard()
            )
            await AppointmentStates.cancel_confirmation.set()


def format_appointment_details(appointment: Appointment) -> str:
    """Форматирование деталей записи"""
    return (
        f"📅 {format_appointment_date(appointment.date)} {appointment.time_slot}\n"
        f"🧔 Барбер: {appointment.barber.name}\n"
        f"✂️ Услуга: {appointment.service.name}\n"
        f"💰 Стоимость: {appointment.service.price} руб."
    )


async def confirm_appointment_cancellation(message: types.Message, state: FSMContext):
    """Подтверждение отмены записи"""
    if message.text.lower() != 'да':
        await message.answer("Отмена записи отменена")
        await state.finish()
        return

    async with state.proxy() as data:
        appointment_id = data['appointment_id']

    with get_db_session() as session:
        appointment = get_appointment_by_id(session, appointment_id)
        cancel_appointment(session, appointment_id)

    await message.answer(
        f"❌ Запись ID {appointment_id} отменена\n"
        f"{format_appointment_details(appointment)}",
        reply_markup=appointments_keyboard()
    )
    await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(
        show_appointments_menu,
        text="Записи",
        is_admin=True
    )
    dp.register_message_handler(
        show_appointments_by_date,
        text=["Сегодня", "Завтра", "Неделя"],
        is_admin=True
    )
    dp.register_callback_query_handler(
        handle_appointment_action,
        lambda c: c.data.startswith(('confirm_app:', 'cancel_app:')),
        is_admin=True
    )
    dp.register_message_handler(
        confirm_appointment_cancellation,
        state=AppointmentStates.cancel_confirmation
    )