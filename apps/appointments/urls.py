from django.urls import path
from .views import (
    AppointmentCreateView, MyAppointmentsView,
    CancelAppointmentView, RescheduleAppointmentView
)

urlpatterns = [
    path("appointments/", AppointmentCreateView.as_view()),
    path("appointments/my/", MyAppointmentsView.as_view()),
    path("appointments/<int:pk>/cancel/", CancelAppointmentView.as_view()),
    path("appointments/<int:pk>/reschedule/", RescheduleAppointmentView.as_view()),
]
