from django.contrib import admin
from .models import Doctor, AvailabilitySlot

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id","first_name","last_name","specialty","room","is_active")
    search_fields = ("first_name","last_name","specialty")

@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ("id","doctor","start_time","duration_minutes","is_available")
    list_filter = ("is_available","doctor")
