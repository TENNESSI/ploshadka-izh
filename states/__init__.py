from .appointment_states import AppointmentStates
from .admin_states import (
    AdminStates,
    BarberManagementStates,
    ServiceManagementStates,
    ScheduleManagementStates
)
from .client_states import (
    ClientRegistrationStates,
    ServiceSelectionStates,
    BarberSelectionStates,
    DateTimeSelectionStates
)

# Экспорт всех состояний для удобного импорта
__all__ = [
    'AppointmentStates',
    'AdminStates',
    'BarberManagementStates',
    'ServiceManagementStates',
    'ScheduleManagementStates',
    'ClientRegistrationStates',
    'ServiceSelectionStates',
    'BarberSelectionStates',
    'DateTimeSelectionStates'
]

# Альтернативный вариант экспорта групп состояний
class AllStates:
    """Контейнер для всех состояний проекта"""
    appointment = AppointmentStates
    admin = AdminStates
    barber_management = BarberManagementStates
    service_management = ServiceManagementStates
    schedule_management = ScheduleManagementStates
    client_registration = ClientRegistrationStates
    service_selection = ServiceSelectionStates
    barber_selection = BarberSelectionStates
    date_time_selection = DateTimeSelectionStates