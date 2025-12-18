from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .models import Doctor, AvailabilitySlot
from .serializers import DoctorSerializer, AvailabilitySlotSerializer

class DoctorListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Doctor.objects.filter(is_active=True).order_by("id")
    serializer_class = DoctorSerializer

class DoctorSlotsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AvailabilitySlotSerializer

    def get_queryset(self):
        doctor_id = self.kwargs["pk"]
        qs = AvailabilitySlot.objects.filter(
            doctor_id=doctor_id,
            is_available=True,
            start_time__gte=timezone.now()
        ).order_by("start_time")
        return qs
