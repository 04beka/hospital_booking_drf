from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import Appointment
from .serializers import AppointmentSerializer

class AdminAppointmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Appointment.objects.select_related("patient","doctor","slot").all().order_by("-created_at")
    serializer_class = AppointmentSerializer
    permission_classes = [IsAdminUser]
