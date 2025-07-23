from .client.start import register_handlers as register_client_handlers
from .admin.panel import register_handlers as register_admin_handlers

def register_all_handlers(dp):
    """Регистрирует все обработчики."""
    register_client_handlers(dp)
    register_admin_handlers(dp)
    # ... остальные модули