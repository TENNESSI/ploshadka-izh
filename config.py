import os
from dotenv import load_dotenv
from typing import List, Dict, Any

#Загрузка переменных окружения из .env
load_dotenv()

class Config:
	"""Основной класс конфигурации"""

	# Telegram Bot
	BOT_TOKEN: str = os.getenv('BOT_TOKEN')
	ADMIN_IDS: List[int] = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]

	# Настройки работы барбершопа
	WORK_START: int = 10 # Час открытия
	WORK_END: int = 20 # Час закрытия
	WORK_DAYS: List[int] = [0, 1, 2, 3, 4, 5] # Пн - Сб (дни недели, 0 - понедельник)
	TIMEZONE: str = 'Europe/Moscow'

	# Настройки базы данных
	DB_NAME: str = os.getenv('DB_NAME', 'barbershop.db')
	DB_PATH: str = os.path.join(os.path.dirname(__file__), 'database', DB_NAME)
	SQLALCHEMY_DATABASE_URI: str = f'sqlite:///{DB_PATH}'

	# Настройки записей
	DEFAULT_APPOINTMENT_DURATION: int = 30 # В МИНУТАХ
	REMINDER_HOURS_BEFORE: int = 24 # за сколько часов напоминать о записи

	