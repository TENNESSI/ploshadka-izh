import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from config import config
from handlers import register_all_handlers
from database.db import init_db
import asyncio

# Настройка логирования
logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logger.info("Бот запускается...")
    await init_db()  # Инициализация базы данных
    logger.info("Бот успешно запущен")


async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("Бот останавливается...")
    logger.info("Бот успешно остановлен")


async def main():
    """Основная функция запуска бота"""
    try:
        # Инициализация бота с настройками по умолчанию
        bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

        # Инициализация диспетчера с хранилищем состояний
        dp = Dispatcher(storage=MemoryStorage())

        # Регистрация обработчиков
        register_all_handlers(dp)

        # Запуск бота
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, on_startup=on_startup, on_shutdown=on_shutdown)

    except Exception as e:
        logger.critical(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    asyncio.run(main())