from aiogram import Bot
from aiogram.types import Message, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from typing import List, Dict, Optional
from config import config
from database.models import Appointment, Barber
import logging
import pytz

logger = logging.getLogger(__name__)


async def send_welcome_message(bot: Bot, chat_id: int):
    """Отправка приветственного сообщения новому пользователю"""
    try:
        text = (
            "👋 Добро пожаловать в *BarberShop*!\n\n"
            "Я помогу вам записаться к нашим барберам в удобное время.\n"
            "Вот что я умею:\n"
            "✂️ Запись на услуги\n"
            "🧔 Выбор барбера\n"
            "📅 Просмотр свободных слотов\n"
            "🔔 Напоминания о записи\n\n"
            "Нажмите /start чтобы начать."
        )
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error sending welcome message: {e}")


async def send_appointment_confirmation(
        bot: Bot,
        chat_id: int,
        appointment: Appointment,
        barber: Barber
):
    """Отправка подтверждения записи"""
    try:
        appointment_date = datetime.strptime(appointment.date, "%Y-%m-%d")
        text = (
            "✅ *Запись подтверждена*\n\n"
            f"📅 *Дата:* {appointment_date.strftime('%d %B %Y')}\n"
            f"⏰ *Время:* {appointment.time_slot}\n"
            f"🧔 *Барбер:* {barber.name}\n"
            f"✂️ *Услуга:* {appointment.service.name}\n"
            f"💵 *Стоимость:* {appointment.service.price} руб.\n\n"
            "Вы можете отменить запись в разделе 'Мои записи'."
        )
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error sending appointment confirmation: {e}")


async def send_reminder(
        bot: Bot,
        chat_id: int,
        appointment: Appointment,
        hours_before: int = 24
):
    """Отправка напоминания о записи"""
    try:
        appointment_date = datetime.strptime(appointment.date, "%Y-%m-%d")
        time_part = appointment.time_slot.split('-')[0]
        appointment_datetime = datetime.strptime(
            f"{appointment.date} {time_part}",
            "%Y-%m-%d %H:%M"
        ).replace(tzinfo=pytz.timezone(config.TIMEZONE))

        text = (
            "🔔 *Напоминание о записи*\n\n"
            f"У вас запись *через {hours_before} час(а/ов)*:\n"
            f"📅 *Дата:* {appointment_date.strftime('%d %B %Y')}\n"
            f"⏰ *Время:* {appointment.time_slot}\n"
            f"🧔 *Барбер:* {appointment.barber.name}\n"
            f"✂️ *Услуга:* {appointment.service.name}\n\n"
            "Пожалуйста, не опаздывайте!"
        )
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error sending reminder: {e}")


async def notify_admins(
        bot: Bot,
        message: str,
        exclude_ids: List[int] = None
):
    """Отправка уведомления всем администраторам"""
    try:
        if not exclude_ids:
            exclude_ids = []

        for admin_id in config.ADMIN_IDS:
            if admin_id not in exclude_ids:
                try:
                    await bot.send_message(
                        chat_id=admin_id,
                        text=f"👨‍💻 *Админ-уведомление:*\n\n{message}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                except Exception as e:
                    logger.error(f"Error notifying admin {admin_id}: {e}")
    except Exception as e:
        logger.error(f"Error in notify_admins: {e}")


async def notify_appointment_cancellation(
        bot: Bot,
        client_id: int,
        appointment: Appointment,
        barber: Barber,
        reason: Optional[str] = None
):
    """Уведомление об отмене записи"""
    try:
        text = (
            "❌ *Запись отменена*\n\n"
            f"📅 Дата: {appointment.date}\n"
            f"⏰ Время: {appointment.time_slot}\n"
            f"🧔 Барбер: {barber.name}\n"
        )
        if reason:
            text += f"\nПричина: {reason}"

        await bot.send_message(
            chat_id=client_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error sending cancellation notification: {e}")


async def send_daily_schedule_to_barbers(
        bot: Bot,
        schedule: Dict[int, List[Appointment]]
):
    """Отправка расписания барберам на день"""
    try:
        for barber_id, appointments in schedule.items():
            if not appointments:
                continue

            barber_appointments = []
            for app in appointments:
                barber_appointments.append(
                    f"⏰ {app.time_slot} - {app.service.name} "
                    f"({app.client_name or f'ID {app.user_id}'})"
                )

            text = (
                    "📅 *Ваше расписание на сегодня*\n\n" +
                    "\n".join(barber_appointments) +
                    "\n\nУдачного рабочего дня!"
            )

            await bot.send_message(
                chat_id=barber_id,
                text=text,
                parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Error sending daily schedule: {e}")


async def send_feedback_request(
        bot: Bot,
        chat_id: int,
        appointment: Appointment,
        barber: Barber
):
    """Запрос отзыва после посещения"""
    try:
        text = (
            "🙂 *Как вам посещение?*\n\n"
            f"Оцените работу барбера *{barber.name}*\n"
            "и оставьте отзыв о качестве услуги."
        )

        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("⭐ 1", callback_data="rate_1"),
            InlineKeyboardButton("⭐ 2", callback_data="rate_2"),
            InlineKeyboardButton("⭐ 3", callback_data="rate_3"),
            InlineKeyboardButton("⭐ 4", callback_data="rate_4"),
            InlineKeyboardButton("⭐ 5", callback_data="rate_5")
        )

        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error sending feedback request: {e}")