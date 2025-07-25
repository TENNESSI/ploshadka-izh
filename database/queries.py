from sqlalchemy import func, and_, or_, extract, not_
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Tuple
from database.models import Barber, Service, Schedule, Appointment
from config import config
import logging


DB_PATH = config.DB_PATH
WORK_START = config.WORK_START
WORK_END = config.WORK_END

logger = logging.getLogger(__name__)


# ====================== БАЗОВЫЕ ФУНКЦИИ ======================

def get_db_session():
    """Создает и возвращает новую сессию БД"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(f'sqlite:///{DB_PATH}')
    Session = sessionmaker(bind=engine)
    return Session()


# ====================== ЗАПРОСЫ ДЛЯ БАРБЕРОВ ======================

def get_barber_by_id(session: Session, barber_id: int) -> Optional[Barber]:
    """Получить барбера по ID"""
    return session.query(Barber).filter(Barber.id == barber_id).first()


def get_active_barbers(session: Session) -> List[Barber]:
    """Получить всех активных барберов"""
    return session.query(Barber).filter(Barber.is_active == True).all()


def add_barber(
        session: Session,
        name: str,
        description: str = None,
        photo_id: str = None
) -> Barber:
    """Добавить нового барбера"""
    try:
        new_barber = Barber(
            name=name,
            description=description,
            photo_id=photo_id
        )
        session.add(new_barber)
        session.commit()
        return new_barber
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding barber: {e}")
        raise


def update_barber(
        session: Session,
        barber_id: int,
        name: str = None,
        description: str = None,
        photo_id: str = None,
        is_active: bool = None
) -> bool:
    """Обновить данные барбера"""
    barber = get_barber_by_id(session, barber_id)
    if not barber:
        return False

    try:
        if name: barber.name = name
        if description: barber.description = description
        if photo_id: barber.photo_id = photo_id
        if is_active is not None: barber.is_active = is_active

        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating barber: {e}")
        return False


# ====================== ЗАПРОСЫ ДЛЯ УСЛУГ ======================

def get_service_by_id(session: Session, service_id: int) -> Optional[Service]:
    """Получить услугу по ID"""
    return session.query(Service).filter(Service.id == service_id).first()


def get_all_services(session: Session, active_only: bool = True) -> List[Service]:
    """Получить все услуги (по умолчанию только активные)"""
    query = session.query(Service)
    if active_only:
        query = query.filter(Service.is_active == True)
    return query.all()


def add_service(
        session: Session,
        name: str,
        duration: int,
        price: int
) -> Service:
    """Добавить новую услугу"""
    try:
        new_service = Service(
            name=name,
            duration=duration,
            price=price
        )
        session.add(new_service)
        session.commit()
        return new_service
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding service: {e}")
        raise


def update_service(
        session: Session,
        service_id: int,
        name: str = None,
        duration: int = None,
        price: int = None,
        is_active: bool = None
) -> bool:
    """Обновить данные услуги"""
    service = get_service_by_id(session, service_id)
    if not service:
        return False

    try:
        if name: service.name = name
        if duration: service.duration = duration
        if price: service.price = price
        if is_active is not None: service.is_active = is_active

        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating service: {e}")
        return False


def delete_service(session: Session, service_id: int) -> bool:
    """Безопасное удаление услуги"""
    service = get_service_by_id(session, service_id)
    if not service:
        return False

    try:
        # Проверяем есть ли связанные записи
        has_appointments = session.query(Appointment).filter(
            Appointment.service_id == service_id
        ).first() is not None

        if has_appointments:
            # Если есть записи - деактивируем
            service.is_active = False
        else:
            # Если нет записей - удаляем полностью
            session.delete(service)

        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting service: {e}")
        return False


# ====================== ЗАПРОСЫ ДЛЯ РАСПИСАНИЯ ======================

def generate_time_slots(duration: int = 30) -> List[str]:
    """Сгенерировать временные слоты на день"""
    slots = []
    current_time = datetime.strptime(f"{WORK_START}:00", "%H:%M")
    end_time = datetime.strptime(f"{WORK_END}:00", "%H:%M")

    while current_time + timedelta(minutes=duration) <= end_time:
        slot_end = current_time + timedelta(minutes=duration)
        slots.append(
            f"{current_time.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}"
        )
        current_time = slot_end

    return slots


def get_available_slots(
        session: Session,
        date: str,
        barber_id: int = None,
        service_id: int = None
) -> List[Schedule]:
    """Получить доступные слоты расписания"""
    query = session.query(Schedule).filter(
        Schedule.date == date,
        Schedule.is_available == True
    )

    if barber_id:
        query = query.filter(Schedule.barber_id == barber_id)

    if service_id:
        service = get_service_by_id(session, service_id)
        if service:
            # Фильтр по продолжительности услуги
            query = query.join(Barber).filter(
                Barber.services.any(id=service_id)
            )

    return query.order_by(Schedule.time_slot).all()


def add_schedule_slot(
        session: Session,
        barber_id: int,
        date: str,
        time_slot: str
) -> Schedule:
    """Добавить слот в расписание"""
    try:
        new_slot = Schedule(
            barber_id=barber_id,
            date=date,
            time_slot=time_slot
        )
        session.add(new_slot)
        session.commit()
        return new_slot
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding schedule slot: {e}")
        raise


def lock_time_slot(
        session: Session,
        barber_id: int,
        date: str,
        time_slot: str
) -> bool:
    """Заблокировать временной слот"""
    slot = session.query(Schedule).filter(
        Schedule.barber_id == barber_id,
        Schedule.date == date,
        Schedule.time_slot == time_slot
    ).first()

    if slot:
        slot.is_available = False
        session.commit()
        return True
    return False


def unlock_time_slot(
        session: Session,
        barber_id: int,
        date: str,
        time_slot: str
) -> bool:
    """Разблокировать временной слот"""
    slot = session.query(Schedule).filter(
        Schedule.barber_id == barber_id,
        Schedule.date == date,
        Schedule.time_slot == time_slot
    ).first()

    if slot:
        slot.is_available = True
        session.commit()
        return True
    return False


# ====================== ЗАПРОСЫ ДЛЯ ЗАПИСЕЙ ======================

def create_appointment(
        session: Session,
        user_id: int,
        barber_id: int,
        service_id: int,
        date: str,
        time_slot: str
) -> Appointment:
    """Создать новую запись клиента"""
    try:
        # Блокируем слот
        slot = session.query(Schedule).filter(
            Schedule.barber_id == barber_id,
            Schedule.date == date,
            Schedule.time_slot == time_slot
        ).first()

        if not slot or not slot.is_available:
            raise ValueError("Time slot not available")

        slot.is_available = False

        # Создаем запись
        new_appointment = Appointment(
            user_id=user_id,
            barber_id=barber_id,
            service_id=service_id,
            date=date,
            time_slot=time_slot,
            status='booked'
        )

        session.add(new_appointment)
        session.commit()
        return new_appointment
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating appointment: {e}")
        raise


def get_appointment_by_id(session: Session, appointment_id: int) -> Optional[Appointment]:
    """Получить запись по ID"""
    return session.query(Appointment).filter(Appointment.id == appointment_id).first()


def get_appointments_by_date(
        session: Session,
        date: str,
        barber_id: int = None,
        service_id: int = None
) -> List[Appointment]:
    """Получить записи на конкретную дату"""
    query = session.query(Appointment).filter(
        Appointment.date == date
    )

    if barber_id:
        query = query.filter(Appointment.barber_id == barber_id)

    if service_id:
        query = query.filter(Appointment.service_id == service_id)

    return query.order_by(Appointment.time_slot).all()


def get_user_appointments(
        session: Session,
        user_id: int,
        upcoming_only: bool = True
) -> List[Appointment]:
    """Получить записи пользователя"""
    query = session.query(Appointment).filter(
        Appointment.user_id == user_id
    )

    if upcoming_only:
        today = datetime.now().strftime("%Y-%m-%d")
        query = query.filter(
            or_(
                Appointment.date > today,
                and_(
                    Appointment.date == today,
                    Appointment.time_slot >= datetime.now().strftime("%H:%M")
                )
            )
        ).filter(
            Appointment.status == 'booked'
        )

    return query.order_by(Appointment.date, Appointment.time_slot).all()


def confirm_appointment(session: Session, appointment_id: int) -> bool:
    """Подтвердить запись клиента"""
    appointment = get_appointment_by_id(session, appointment_id)
    if appointment:
        appointment.status = 'confirmed'
        session.commit()
        return True
    return False


def cancel_appointment(session: Session, appointment_id: int) -> bool:
    """Отменить запись клиента"""
    appointment = get_appointment_by_id(session, appointment_id)
    if not appointment:
        return False

    try:
        appointment.status = 'canceled'

        # Разблокируем слот
        slot = session.query(Schedule).filter(
            Schedule.barber_id == appointment.barber_id,
            Schedule.date == appointment.date,
            Schedule.time_slot == appointment.time_slot
        ).first()

        if slot:
            slot.is_available = True

        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Error canceling appointment: {e}")
        return False


# ====================== ЗАПРОСЫ ДЛЯ АДМИНИСТРИРОВАНИЯ ======================

def get_admin_stats(
        session: Session,
        start_date: str,
        end_date: str
) -> Dict[str, any]:
    """Получить статистику для админ-панели"""
    stats = {
        'total_appointments': 0,
        'completed_services': 0,
        'canceled_appointments': 0,
        'total_income': 0,
        'popular_services': [],
        'busy_days': []
    }

    try:
        # Общая статистика
        stats['total_appointments'] = session.query(Appointment).filter(
            Appointment.date.between(start_date, end_date)
        ).count()

        stats['completed_services'] = session.query(Appointment).filter(
            Appointment.date.between(start_date, end_date),
            Appointment.status == 'completed'
        ).count()

        stats['canceled_appointments'] = session.query(Appointment).filter(
            Appointment.date.between(start_date, end_date),
            Appointment.status == 'canceled'
        ).count()

        # Общий доход
        income = session.query(
            func.sum(Service.price)
        ).join(
            Appointment.service
        ).filter(
            Appointment.date.between(start_date, end_date),
            Appointment.status == 'completed'
        ).scalar()

        stats['total_income'] = income if income else 0

        # Популярные услуги (топ-5)
        stats['popular_services'] = session.query(
            Service.name,
            func.count(Appointment.id).label('count')
        ).join(
            Appointment.service
        ).filter(
            Appointment.date.between(start_date, end_date),
            Appointment.status == 'completed'
        ).group_by(
            Service.name
        ).order_by(
            func.count(Appointment.id).desc()
        ).limit(5).all()

        # Самые загруженные дни (топ-5)
        stats['busy_days'] = session.query(
            Appointment.date,
            func.count(Appointment.id).label('count')
        ).filter(
            Appointment.date.between(start_date, end_date),
            Appointment.status.in_(['booked', 'confirmed'])
        ).group_by(
            Appointment.date
        ).order_by(
            func.count(Appointment.id).desc()
        ).limit(5).all()

    except Exception as e:
        logger.error(f"Error getting stats: {e}")

    return stats