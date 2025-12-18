from rest_framework import serializers
from .models import Doctor, AvailabilitySlot

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["id","first_name","last_name","specialty","room","is_active"]

class AvailabilitySlotSerializer(serializers.ModelSerializer):
    end_time = serializers.DateTimeField(read_only=True)  # source წაშლილია

    class Meta:
        model = AvailabilitySlot
        fields = ["id", "doctor", "start_time", "duration_minutes", "is_available", "end_time"]
