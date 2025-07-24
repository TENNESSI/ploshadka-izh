from sqlalchemy import (
    Column, Integer, String, Boolean,
    ForeignKey, DateTime, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Базовый класс для моделей
Base = declarative_base()

class Barber(Base):
    """Модель специалиста"""
    __tablename__ = 'barbers'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
    photo_id = Column(String(150))  # ID фото в Telegram
    is_active = Column(Boolean, default=True)

    # Связь с расписанием и записями
    schedule = relationship("Schedule", back_populates="barber")
    appointments = relationship("Appointment", back_populates="barber")

    def __repr__(self):
        return f"<Barber(id={self.id}, name='{self.name}')>"


class Service(Base):
    """Модель услуги."""
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    duration = Column(Integer, nullable=False)  # В минутах
    price = Column(Integer, nullable=False)     # В рублях
    is_active = Column(Boolean, default=True)  # Флаг активности услуги

    # Связь с записями
    appointments = relationship("Appointment", back_populates="service")

    def __repr__(self):
        return f"<Service(id={self.id}, name='{self.name}')>"


class Schedule(Base):
    """Модель расписания (свободные слоты)."""
    __tablename__ = 'schedule'

    id = Column(Integer, primary_key=True)
    barber_id = Column(Integer, ForeignKey('barbers.id'), nullable=False)
    date = Column(String(10), nullable=False)       # Формат: 'YYYY-MM-DD'
    time_slot = Column(String(11), nullable=False)  # Формат: 'HH:MM-HH:MM'
    is_available = Column(Boolean, default=True)

    # Связь с барбером
    barber = relationship("Barber", back_populates="schedule")

    def __repr__(self):
        return f"<Schedule(id={self.id}, barber_id={self.barber_id}, slot='{self.time_slot}')>"


class Appointment(Base):
    """Модель записи клиента."""
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # ID пользователя в Telegram
    barber_id = Column(Integer, ForeignKey('barbers.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    date = Column(String(10), nullable=False)
    time_slot = Column(String(11), nullable=False)
    status = Column(String(20), default='booked')  # booked/canceled/completed
    created_at = Column(DateTime, default=datetime.now)

    # Связи
    barber = relationship("Barber", back_populates="appointments")
    service = relationship("Service", back_populates="appointments")

    def __repr__(self):
        return f"<Appointment(id={self.id}, user_id={self.user_id}, date='{self.date}')>"