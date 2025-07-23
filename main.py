from aiogram import executor
from handlers.client import start
from handlers.admin import panel
from database.db import init_db

def setup_handlers(dp):
    """Регистрация всех обработчиков."""
    start.register_handlers(dp)
    panel.register_handlers(dp)

if __name__ == '__main__':
    init_db()  # Создаём таблицы при первом запуске
    executor.start_polling(dp, skip_updates=True)