from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import Doctor, AvailabilitySlot
from .serializers import DoctorSerializer, AvailabilitySlotSerializer

class AdminDoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all().order_by("-id")
    serializer_class = DoctorSerializer
    permission_classes = [IsAdminUser]

class AdminSlotViewSet(viewsets.ModelViewSet):
    queryset = AvailabilitySlot.objects.all().order_by("-start_time")
    serializer_class = AvailabilitySlotSerializer
    permission_classes = [IsAdminUser]
