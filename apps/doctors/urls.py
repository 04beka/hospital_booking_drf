from django.urls import path
from .views import DoctorListView, DoctorSlotsView

urlpatterns = [
    path("doctors/", DoctorListView.as_view()),
    path("doctors/<int:pk>/slots/", DoctorSlotsView.as_view()),
]
