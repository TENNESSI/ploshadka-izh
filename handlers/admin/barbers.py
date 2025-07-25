from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from database.models import Barber
from database.db import Session
from states import BarberAddStates
from keyboards.admin import (
    barbers_keyboard,
    confirm_keyboard,
    cancel_keyboard
)
from utils.notifications import notify_admins


# Добавление нового барбера
async def add_barber_start(message: types.Message):
    """Начало процесса добавления барбера"""
    await message.answer(
        "Введите имя нового барбера:",
        reply_markup=cancel_keyboard()
    )
    await BarberAddStates.waiting_for_name.set()


async def process_barber_name(message: types.Message, state: FSMContext):
    """Обработка имени барбера"""
    async with state.proxy() as data:
        data['name'] = message.text

    await BarberAddStates.next()
    await message.answer(
        "Введите описание барбера:",
        reply_markup=cancel_keyboard()
    )


async def process_barber_description(message: types.Message, state: FSMContext):
    """Обработка описания барбера"""
    async with state.proxy() as data:
        data['description'] = message.text

    await BarberAddStates.next()
    await message.answer(
        "Отправьте фото барбера:",
        reply_markup=cancel_keyboard()
    )


async def process_barber_photo(message: types.Message, state: FSMContext):
    """Обработка фото барбера"""
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото!")
        return

    async with state.proxy() as data:
        data['photo_id'] = message.photo[-1].file_id

        # Формируем сообщение для подтверждения
        confirm_message = (
            f"Добавить нового барбера?\n\n"
            f"Имя: {data['name']}\n"
            f"Описание: {data['description']}"
        )

    await BarberAddStates.next()
    await message.answer_photo(
        photo=data['photo_id'],
        caption=confirm_message,
        reply_markup=confirm_keyboard()
    )


async def confirm_add_barber(message: types.Message, state: FSMContext):
    """Подтверждение добавления барбера"""
    if message.text.lower() != 'да':
        await message.answer("Добавление отменено", reply_markup=barbers_keyboard())
        await state.finish()
        return

    async with state.proxy() as data:
        with Session() as session:
            new_barber = Barber(
                name=data['name'],
                description=data['description'],
                photo_id=data['photo_id']
            )
            session.add(new_barber)
            session.commit()

    await message.answer(
        "Барбер успешно добавлен!",
        reply_markup=barbers_keyboard()
    )
    await state.finish()
    await notify_admins(f"Добавлен новый барбер: {data['name']}")


# Удаление барбера
async def delete_barber_start(message: types.Message):
    """Начало процесса удаления барбера"""
    with Session() as session:
        barbers = session.query(Barber).filter(Barber.is_active == True).all()

    if not barbers:
        await message.answer("Нет активных барберов для удаления")
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for barber in barbers:
        keyboard.add(f"Удалить {barber.name}")
    keyboard.add("Отмена")

    await message.answer(
        "Выберите барбера для удаления:",
        reply_markup=keyboard
    )
    await BarberAddStates.waiting_for_deletion.set()


async def process_barber_deletion(message: types.Message, state: FSMContext):
    """Обработка удаления барбера"""
    if message.text == "Отмена":
        await message.answer("Отменено", reply_markup=barbers_keyboard())
        await state.finish()
        return

    barber_name = message.text.replace("Удалить ", "")
    with Session() as session:
        barber = session.query(Barber).filter(
            Barber.name == barber_name,
            Barber.is_active == True
        ).first()

        if barber:
            barber.is_active = False
            session.commit()
            await message.answer(
                f"Барбер {barber_name} деактивирован",
                reply_markup=barbers_keyboard()
            )
            await notify_admins(f"Барбер {barber_name} деактивирован")
        else:
            await message.answer("Барбер не найден")

    await state.finish()


# Список барберов
async def show_barbers(message: types.Message):
    """Показать всех активных барберов"""
    with Session() as session:
        barbers = session.query(Barber).filter(Barber.is_active == True).all()

    if not barbers:
        await message.answer("Нет активных барберов")
        return

    for barber in barbers:
        caption = f"{barber.name}\n\n{barber.description or 'Нет описания'}"
        try:
            await message.answer_photo(
                photo=barber.photo_id,
                caption=caption
            )
        except:
            await message.answer(caption)


# Регистрация обработчиков
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(
        add_barber_start,
        text="Добавить барбера",
        is_admin=True
    )
    dp.register_message_handler(
        delete_barber_start,
        text="Удалить барбера",
        is_admin=True
    )
    dp.register_message_handler(
        show_barbers,
        text="Список барберов",
        is_admin=True
    )

    # FSM обработчики
    dp.register_message_handler(
        process_barber_name,
        state=BarberAddStates.waiting_for_name
    )
    dp.register_message_handler(
        process_barber_description,
        state=BarberAddStates.waiting_for_description
    )
    dp.register_message_handler(
        process_barber_photo,
        content_types=['photo'],
        state=BarberAddStates.waiting_for_photo
    )
    dp.register_message_handler(
        confirm_add_barber,
        state=BarberAddStates.waiting_for_confirmation
    )
    dp.register_message_handler(
        process_barber_deletion,
        state=BarberAddStates.waiting_for_deletion
    )