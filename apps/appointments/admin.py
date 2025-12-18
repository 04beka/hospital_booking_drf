from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id","patient","doctor","slot","status","created_at")
    list_filter = ("status","doctor")
    search_fields = ("patient__email",)
