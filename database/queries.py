from sqlalchemy.orm import Session
from database.models import Barber, Service, Schedule, Appointment

# --- Запросы для барберов ---
def get_active_barbers(db: Session) -> list[Barber]:
    """Получить всех активных барберов."""
    return db.query(Barber).filter(Barber.is_active == True).all()

def get_barber_by_id(db: Session, barber_id: int) -> Barber | None:
    """Найти барбера по ID."""
    return db.query(Barber).filter(Barber.id == barber_id).first()

# --- Запросы для расписания ---
def get_available_slots(db: Session, date: str) -> list[Schedule]:
    """Получить свободные слоты на дату."""
    return (
        db.query(Schedule)
        .filter(Schedule.date == date, Schedule.is_available == True)
        .all()
    )

# --- Запросы для записей ---
def create_appointment(
    db: Session,
    user_id: int,
    barber_id: int,
    service_id: int,
    date: str,
    time_slot: str
) -> Appointment:
    """Создать новую запись."""
    appointment = Appointment(
        user_id=user_id,
        barber_id=barber_id,
        service_id=service_id,
        date=date,
        time_slot=time_slot
    )
    db.add(appointment)
    db.commit()
    return appointment