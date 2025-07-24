from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from database.queries import get_admin_stats
from keyboards.admin import (
    admin_main_keyboard,
    admin_management_keyboard,
    stats_keyboard
)
from utils.date_utils import get_month_range


# Главное меню админа
async def show_admin_panel(message: types.Message):
    """Показывает главное меню администратора"""
    await message.answer(
        "⚙️ Панель администратора",
        reply_markup=admin_main_keyboard()
    )


# Управление компонентами
async def show_management_menu(message: types.Message):
    """Меню управления основными компонентами"""
    await message.answer(
        "🛠 Управление компонентами:",
        reply_markup=admin_management_keyboard()
    )


# Статистика
async def show_stats_menu(message: types.Message):
    """Меню просмотра статистики"""
    await message.answer(
        "📊 Выберите период для статистики:",
        reply_markup=stats_keyboard()
    )


async def show_current_month_stats(message: types.Message):
    """Показывает статистику за текущий месяц"""
    start_date, end_date = get_month_range()
    stats = await get_admin_stats(start_date, end_date)

    stats_message = (
        f"📈 Статистика за текущий месяц:\n\n"
        f"• Новые записи: {stats['new_appointments']}\n"
        f"• Завершенные услуги: {stats['completed_services']}\n"
        f"• Отмененные записи: {stats['canceled_appointments']}\n"
        f"• Общий доход: {stats['total_income']} руб.\n\n"
        f"📅 Период: {start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')}"
    )

    await message.answer(stats_message)


# Выход из админки
async def exit_admin_panel(message: types.Message):
    """Выход из режима администратора"""
    await message.answer(
        "Вы вышли из панели администратора",
        reply_markup=types.ReplyKeyboardRemove()
    )


# Регистрация обработчиков
def register_handlers(dp: Dispatcher):
    # Команда /admin
    dp.register_message_handler(
        show_admin_panel,
        commands=["admin"],
        is_admin=True
    )

    # Главное меню
    dp.register_message_handler(
        show_admin_panel,
        Text(equals="Админ панель", ignore_case=True),
        is_admin=True
    )

    # Подменю
    dp.register_message_handler(
        show_management_menu,
        Text(equals="Управление", ignore_case=True),
        is_admin=True
    )

    dp.register_message_handler(
        show_stats_menu,
        Text(equals="Статистика", ignore_case=True),
        is_admin=True
    )

    dp.register_message_handler(
        show_current_month_stats,
        Text(equals="Текущий месяц", ignore_case=True),
        is_admin=True
    )

    dp.register_message_handler(
        exit_admin_panel,
        Text(equals="Выйти из админки", ignore_case=True),
        is_admin=True
    )