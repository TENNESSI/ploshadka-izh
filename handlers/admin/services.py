from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database.queries import (
    get_db_session,
    get_all_services,
    get_service_by_id,
    add_service,
    delete_service
)
from keyboards.admin import (
    services_keyboard,
    service_actions_keyboard,
    confirm_keyboard,
    cancel_keyboard
)
from utils.notifications import notify_admins


class ServiceStates(StatesGroup):
    """FSM состояния для управления услугами"""
    waiting_for_name = State()
    waiting_for_duration = State()
    waiting_for_price = State()
    waiting_for_confirmation = State()
    waiting_for_deletion = State()


# Меню услуг
async def show_services_menu(message: types.Message):
    """Показать меню управления услугами"""
    await message.answer(
        "✂️ Управление услугами:",
        reply_markup=services_keyboard()
    )


# Добавление новой услуги
async def add_service_start(message: types.Message):
    """Начало процесса добавления услуги"""
    await message.answer(
        "Введите название новой услуги:",
        reply_markup=cancel_keyboard()
    )
    await ServiceStates.waiting_for_name.set()


async def process_service_name(message: types.Message, state: FSMContext):
    """Обработка названия услуги"""
    async with state.proxy() as data:
        data['name'] = message.text

    await ServiceStates.next()
    await message.answer(
        "Введите продолжительность услуги в минутах:",
        reply_markup=cancel_keyboard()
    )


async def process_service_duration(message: types.Message, state: FSMContext):
    """Обработка продолжительности услуги"""
    try:
        duration = int(message.text)
        if duration <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число минут!")
        return

    async with state.proxy() as data:
        data['duration'] = duration

    await ServiceStates.next()
    await message.answer(
        "Введите стоимость услуги в рублях:",
        reply_markup=cancel_keyboard()
    )


async def process_service_price(message: types.Message, state: FSMContext):
    """Обработка стоимости услуги"""
    try:
        price = int(message.text)
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму!")
        return

    async with state.proxy() as data:
        data['price'] = price

        confirm_message = (
            f"Подтвердите данные новой услуги:\n\n"
            f"Название: {data['name']}\n"
            f"Длительность: {data['duration']} мин.\n"
            f"Стоимость: {data['price']} руб."
        )

    await ServiceStates.next()
    await message.answer(
        confirm_message,
        reply_markup=confirm_keyboard()
    )


async def confirm_add_service(message: types.Message, state: FSMContext):
    """Подтверждение добавления услуги"""
    if message.text.lower() != 'да':
        await message.answer("Добавление отменено", reply_markup=services_keyboard())
        await state.finish()
        return

    async with state.proxy() as data:
        with get_db_session() as session:
            new_service = add_service(
                session=session,
                name=data['name'],
                duration=data['duration'],
                price=data['price']
            )

    await message.answer(
        f"Услуга «{new_service.name}» успешно добавлена!",
        reply_markup=services_keyboard()
    )
    await state.finish()
    await notify_admins(f"Добавлена новая услуга: {new_service.name}")


# Удаление услуги
async def delete_service_start(message: types.Message):
    """Начало процесса удаления услуги"""
    with get_db_session() as session:
        services = get_all_services(session)

    if not services:
        await message.answer("Нет доступных услуг для удаления")
        return

    services_text = "\n".join([f"{s.id}. {s.name} ({s.price} руб.)" for s in services])
    await message.answer(
        f"Список услуг:\n\n{services_text}\n\n"
        "Введите ID услуги для удаления:",
        reply_markup=cancel_keyboard()
    )
    await ServiceStates.waiting_for_deletion.set()


async def process_service_deletion(message: types.Message, state: FSMContext):
    """Обработка удаления услуги"""
    if message.text == "Отмена":
        await message.answer("Отменено", reply_markup=services_keyboard())
        await state.finish()
        return

    try:
        service_id = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите числовой ID!")
        return

    with get_db_session() as session:
        service = get_service_by_id(session, service_id)
        if not service:
            await message.answer("Услуга с таким ID не найдена!")
            await state.finish()
            return

        try:
            success = delete_service(session, service_id)
            if success:
                await message.answer(
                    f"Услуга «{service.name}» полностью удалена!",
                    reply_markup=services_keyboard()
                )
            else:
                await message.answer(
                    f"Услуга «{service.name}» деактивирована (есть связанные записи)!",
                    reply_markup=services_keyboard()
                )
            await notify_admins(f"Удалена услуга: {service.name}")
        except Exception as e:
            await message.answer(
                f"Ошибка при удалении: {str(e)}",
                reply_markup=services_keyboard()
            )

        await state.finish()


# Просмотр списка услуг
async def show_services_list(message: types.Message):
    """Показать список всех услуг"""
    with get_db_session() as session:
        services = get_all_services(session)

    if not services:
        await message.answer("Список услуг пуст")
        return

    response = ["Список доступных услуг:\n"]
    for service in services:
        response.append(
            f"\n✂️ {service.name}\n"
            f"⏱ {service.duration} мин. | 💵 {service.price} руб.\n"
            f"ID: {service.id}"
        )

    await message.answer("\n".join(response))


# Регистрация обработчиков
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(
        show_services_menu,
        text="Услуги",
        is_admin=True
    )

    dp.register_message_handler(
        add_service_start,
        text="Добавить услугу",
        is_admin=True
    )

    dp.register_message_handler(
        delete_service_start,
        text="Удалить услугу",
        is_admin=True
    )

    dp.register_message_handler(
        show_services_list,
        text="Список услуг",
        is_admin=True
    )

    # FSM обработчики
    dp.register_message_handler(
        process_service_name,
        state=ServiceStates.waiting_for_name
    )

    dp.register_message_handler(
        process_service_duration,
        state=ServiceStates.waiting_for_duration
    )

    dp.register_message_handler(
        process_service_price,
        state=ServiceStates.waiting_for_price
    )

    dp.register_message_handler(
        confirm_add_service,
        state=ServiceStates.waiting_for_confirmation
    )

    dp.register_message_handler(
        process_service_deletion,
        state=ServiceStates.waiting_for_deletion
    )