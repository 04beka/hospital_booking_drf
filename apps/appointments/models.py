from django.db import models
from django.utils import timezone
from apps.doctors.models import Doctor, AvailabilitySlot
from django.conf import settings

class AppointmentStatus(models.TextChoices):
    BOOKED = "BOOKED", "Booked"
    CANCELLED = "CANCELLED", "Cancelled"
    RESCHEDULED = "RESCHEDULED", "Rescheduled"

class Appointment(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    slot = models.OneToOneField(AvailabilitySlot, on_delete=models.PROTECT, related_name="appointment")

    status = models.CharField(max_length=16, choices=AppointmentStatus.choices, default=AppointmentStatus.BOOKED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.patient.email} -> {self.doctor} @ {self.slot.start_time.isoformat()}"
