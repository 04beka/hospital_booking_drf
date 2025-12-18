from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from .models import Appointment, AppointmentStatus
from .serializers import (
    AppointmentCreateSerializer, AppointmentSerializer,
    AppointmentRescheduleSerializer
)

class AppointmentCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentCreateSerializer

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        appt = ser.save()
        out = AppointmentSerializer(appt)
        return Response(out.data, status=status.HTTP_201_CREATED)

class MyAppointmentsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user).select_related("doctor","slot").order_by("-created_at")

class CancelAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        try:
            appt = Appointment.objects.select_related("slot").get(pk=pk, patient=request.user)
        except Appointment.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        if appt.status == AppointmentStatus.CANCELLED:
            return Response({"detail": "Already cancelled"}, status=400)

        if appt.slot.start_time - timezone.now() < timedelta(hours=2):
            return Response({"detail": "Cannot cancel within 2 hours of appointment"}, status=400)

        appt.status = AppointmentStatus.CANCELLED
        appt.cancelled_at = timezone.now()
        appt.save(update_fields=["status","cancelled_at"])

        appt.slot.is_available = True
        appt.slot.save(update_fields=["is_available"])

        return Response({"message": "Cancelled"}, status=200)

class RescheduleAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        try:
            appt = Appointment.objects.select_related("slot","doctor").get(pk=pk, patient=request.user)
        except Appointment.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        ser = AppointmentRescheduleSerializer(
            data=request.data,
            context={"request": request, "appointment": appt}
        )
        ser.is_valid(raise_exception=True)
        new_slot = ser.validated_data["new_slot"]

        # Free old slot
        old_slot = appt.slot
        old_slot.is_available = True
        old_slot.save(update_fields=["is_available"])

        # Assign new slot
        appt.slot = new_slot
        appt.doctor = new_slot.doctor
        appt.status = AppointmentStatus.RESCHEDULED
        appt.save(update_fields=["slot","doctor","status"])

        new_slot.is_available = False
        new_slot.save(update_fields=["is_available"])

        return Response(AppointmentSerializer(appt).data, status=200)
