from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from database.queries import get_db_session
from keyboards.client import (
    main_menu_keyboard,
    services_menu_keyboard,
    barbers_menu_keyboard
)
from utils.notifications import send_welcome_message


async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await send_welcome_message(message)

    with get_db_session() as session:
        # Проверяем, есть ли пользователь в базе
        # Здесь может быть ваша логика проверки/регистрации пользователя

        await message.answer(
            "🪒 Добро пожаловать в наш барбершоп!\n\n"
            "Выберите действие в меню ниже:",
            reply_markup=main_menu_keyboard()
        )


async def show_main_menu(message: types.Message):
    """Показать главное меню"""
    await message.answer(
        "Главное меню:",
        reply_markup=main_menu_keyboard()
    )


async def show_services_menu(message: types.Message):
    """Показать меню услуг"""
    with get_db_session() as session:
        # Здесь можно получить список услуг из базы
        await message.answer(
            "✂️ Наши услуги:",
            reply_mup=services_menu_keyboard()
        )


async def show_barbers_menu(message: types.Message):
    """Показать меню барберов"""
    with get_db_session() as session:
        # Здесь можно получить список барберов из базы
        await message.answer(
            "🧔 Наши барберы:",
            reply_markup=barbers_menu_keyboard()
        )


async def show_contacts(message: types.Message):
    """Показать контакты"""
    await message.answer(
        "📞 Наши контакты:\n\n"
        "📍 Адрес: ул. Примерная, 123\n"
        "📱 Телефон: +7 (XXX) XXX-XX-XX\n"
        "🕒 Часы работы: 10:00 - 20:00\n\n"
        "Мы в соцсетях:\n"
        "Instagram: @barbershop_example\n"
        "VK: vk.com/barbershop_example"
    )


async def show_about(message: types.Message):
    """Показать информацию о барбершопе"""
    await message.answer(
        "ℹ️ О нашем барбершопе:\n\n"
        "Мы - современный мужской барбершоп с атмосферой настоящего мужского клуба.\n"
        "Используем только профессиональные инструменты и средства.\n"
        "Каждый мастер - профессионал с многолетним опытом."
    )


def register_handlers(dp: Dispatcher):
    """Регистрация обработчиков"""
    dp.register_message_handler(
        cmd_start,
        commands=['start'],
        state='*'
    )
    dp.register_message_handler(
        show_main_menu,
        text="Главное меню",
        state='*'
    )
    dp.register_message_handler(
        show_services_menu,
        text="Услуги",
        state='*'
    )
    dp.register_message_handler(
        show_barbers_menu,
        text="Барберы",
        state='*'
    )
    dp.register_message_handler(
        show_contacts,
        text="Контакты",
        state='*'
    )
    dp.register_message_handler(
        show_about,
        text="О нас",
        state='*'
    )