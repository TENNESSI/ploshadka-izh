from pathlib import Path

BASE_DIR = Path(__file__).parent

# Путь к SQLite БД
DB_PATH = BASE_DIR / "database" / "barber.db"

# Время работы барбершопа (для генерации слотов)
WORK_START = 10  # 10:00
WORK_END = 20    # 20:00