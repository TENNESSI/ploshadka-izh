from .start import register_handlers as register_start_handlers
from .appointment import register_handlers as register_appointment_handlers

def register_handlers(dp):
    register_start_handlers(dp)
    register_appointment_handlers(dp)