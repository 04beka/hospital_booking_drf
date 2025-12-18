from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, VerifyEmailView, ResendCodeView,
    LoginView, RecoveryVerifyView,
    PasswordResetRequestView, PasswordResetConfirmView
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("verify-email/", VerifyEmailView.as_view()),
    path("resend-code/", ResendCodeView.as_view()),
    path("token/", LoginView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("recovery/verify/", RecoveryVerifyView.as_view()),
    path("password-reset/request/", PasswordResetRequestView.as_view()),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view()),
]
