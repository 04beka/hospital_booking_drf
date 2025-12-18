from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.accounts.admin_views import AdminUserViewSet
from apps.doctors.admin_views import AdminDoctorViewSet, AdminSlotViewSet
from apps.appointments.admin_views import AdminAppointmentViewSet

router = DefaultRouter()
router.register(r"admin/users", AdminUserViewSet, basename="admin-users")
router.register(r"admin/doctors", AdminDoctorViewSet, basename="admin-doctors")
router.register(r"admin/slots", AdminSlotViewSet, basename="admin-slots")
router.register(r"admin/appointments", AdminAppointmentViewSet, basename="admin-appointments")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("apps.accounts.urls")),
    path("", include("apps.doctors.urls")),
    path("", include("apps.appointments.urls")),
]
