from sqlite3 import connect, Connection
from config import config

DB_PATH = config.DB_PATH

def get_db() -> Connection:
    """Возвращает подключение к SQLite."""
    return connect(DB_PATH)


def init_db():
    """Создаёт таблицы при первом запуске."""
    with get_db() as db:
        cursor = db.cursor()

        # Специалисты
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS barbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            photo_id TEXT,
            is_active BOOLEAN DEFAULT TRUE
        )
        """)

        # Услуги
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            duration INTEGER NOT NULL,  # в минутах
            price INTEGER NOT NULL
        )
        """)

        # Расписание (слоты)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barber_id INTEGER NOT NULL,
            date TEXT NOT NULL,       # 'YYYY-MM-DD'
            time_slot TEXT NOT NULL,   # 'HH:MM-HH:MM'
            is_available BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (barber_id) REFERENCES barbers (id)
        )
        """)

        # Записи клиентов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            barber_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            status TEXT DEFAULT 'booked',  # 'booked' / 'canceled' / 'completed'
            FOREIGN KEY (barber_id) REFERENCES barbers (id),
            FOREIGN KEY (service_id) REFERENCES services (id)
        )
        """)

        db.commit()