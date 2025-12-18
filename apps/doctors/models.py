from django.db import models
from django.utils import timezone

class Doctor(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    specialty = models.CharField(max_length=120, blank=True)
    room = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class AvailabilitySlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="slots")
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["doctor","start_time"], name="uniq_doctor_start_time")
        ]
        indexes = [
            models.Index(fields=["doctor","start_time"]),
        ]

    @property
    def end_time(self):
        from datetime import timedelta
        return self.start_time + timedelta(minutes=self.duration_minutes)

    def __str__(self):
        return f"{self.doctor} @ {self.start_time.isoformat()}"
