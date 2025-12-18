from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Appointment, AppointmentStatus
from apps.doctors.models import AvailabilitySlot

class AppointmentCreateSerializer(serializers.Serializer):
    slot_id = serializers.IntegerField()

    def validate(self, attrs):
        user = self.context["request"].user
        if not getattr(user, "is_email_verified", False):
            raise serializers.ValidationError("Email must be verified to book.")
        try:
            slot = AvailabilitySlot.objects.select_related("doctor").get(pk=attrs["slot_id"])
        except AvailabilitySlot.DoesNotExist:
            raise serializers.ValidationError({"slot_id": "Slot not found"})
        if not slot.is_available:
            raise serializers.ValidationError({"slot_id": "Slot is not available"})
        if slot.start_time < timezone.now():
            raise serializers.ValidationError({"slot_id": "Slot is in the past"})
        attrs["slot"] = slot
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        slot = validated_data["slot"]
        appt = Appointment.objects.create(
            patient=user,
            doctor=slot.doctor,
            slot=slot,
            status=AppointmentStatus.BOOKED
        )
        slot.is_available = False
        slot.save(update_fields=["is_available"])
        return appt

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    start_time = serializers.DateTimeField(source="slot.start_time", read_only=True)

    class Meta:
        model = Appointment
        fields = ["id","doctor","doctor_name","slot","start_time","status","created_at","updated_at","cancelled_at"]

    def get_doctor_name(self, obj):
        return f"{obj.doctor.first_name} {obj.doctor.last_name}"

class AppointmentCancelSerializer(serializers.Serializer):
    # no input
    pass

class AppointmentRescheduleSerializer(serializers.Serializer):
    new_slot_id = serializers.IntegerField()

    def validate(self, attrs):
        request = self.context["request"]
        appt: Appointment = self.context["appointment"]
        user = request.user

        if appt.patient_id != user.id:
            raise serializers.ValidationError("Not your appointment")

        # 2 hour rule
        if appt.slot.start_time - timezone.now() < timedelta(hours=2):
            raise serializers.ValidationError("Cannot reschedule within 2 hours of appointment")

        try:
            new_slot = AvailabilitySlot.objects.select_related("doctor").get(pk=attrs["new_slot_id"])
        except AvailabilitySlot.DoesNotExist:
            raise serializers.ValidationError({"new_slot_id": "Slot not found"})

        if not new_slot.is_available:
            raise serializers.ValidationError({"new_slot_id": "Slot not available"})
        if new_slot.start_time < timezone.now():
            raise serializers.ValidationError({"new_slot_id": "Slot is in the past"})

        attrs["new_slot"] = new_slot
        return attrs
