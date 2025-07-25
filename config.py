import os
from dotenv import load_dotenv
from typing import List, Dict

# Загрузка переменных окружения из .env файла
load_dotenv()


class Config:
    """Основной класс конфигурации"""

    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    ADMIN_IDS: List[int] = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]

    # Настройки работы барбершопа
    WORK_START: int = 10  # Час открытия (10:00)
    WORK_END: int = 20  # Час закрытия (20:00)
    WORK_DAYS: List[int] = [0, 1, 2, 3, 4, 5]  # Пн-Сб (0 - понедельник)
    TIMEZONE: str = "Europe/Moscow"

    # Настройки базы данных
    DB_NAME: str = os.getenv("DB_NAME", "barbershop.db")
    DB_PATH: str = os.path.join(os.path.dirname(__file__), "database", DB_NAME)
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{DB_PATH}"

    # Настройки записей
    DEFAULT_APPOINTMENT_DURATION: int = 30  # в минутах
    REMINDER_HOURS_BEFORE: int = 24  # за сколько часов напоминать

    # Настройки логирования
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.path.join(os.path.dirname(__file__), "logs", "bot.log")

    # Дополнительные настройки
    BARBER_PHOTO_DIR: str = os.path.join(os.path.dirname(__file__), "static", "barbers")
    SERVICE_PHOTO_DIR: str = os.path.join(os.path.dirname(__file__), "static", "services")

    @classmethod
    def get_work_hours(cls) -> Dict[str, int]:
        """Получить часы работы в виде словаря"""
        return {
            "start": cls.WORK_START,
            "end": cls.WORK_END
        }

    @classmethod
    def validate_config(cls) -> bool:
        """Проверить обязательные настройки"""
        required = [
            cls.BOT_TOKEN,
            cls.ADMIN_IDS
        ]

        if not all(required):
            missing = [name for name, value in vars(cls).items()
                       if not value and not name.startswith('__')]
            raise ValueError(f"Missing required configs: {missing}")

        return True


# Создаем экземпляр конфига
config = Config()

# Проверяем обязательные параметры при импорте
config.validate_config()