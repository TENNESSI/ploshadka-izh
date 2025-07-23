from .panel import register_handlers as register_panel_handlers
from .barbers import register_handlers as register_barbers_handlers
from .services import register_handlers as register_services_handlers
from .schedule import register_handlers as register_schedule_handlers

def register_admin_handlers(dp):
    """Регистрирует ВСЕ административные обработчики."""
    register_panel_handlers(dp)      # /admin и главное меню
    register_barbers_handlers(dp)    # Барберы
    register_services_handlers(dp)   # Услуги
    register_schedule_handlers(dp)   # Расписание