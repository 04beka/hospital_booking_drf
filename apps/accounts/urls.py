from django.urls import path

from .views import (
    RegisterView,
    VerifyEmailView,
    ResendCodeView,
    LoginView,
    RecoveryVerifyView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    MeDeleteView,
    RestoreRequestView,
    RestoreConfirmView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("resend-code/", ResendCodeView.as_view(), name="resend-code"),
    path("login/", LoginView.as_view(), name="login"),

    path("recovery/verify/", RecoveryVerifyView.as_view(), name="recovery-verify"),
    path("password-reset/request/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),

    path("me/delete/", MeDeleteView.as_view(), name="me-delete"),
    path("restore/request/", RestoreRequestView.as_view(), name="restore-request"),
    path("restore/confirm/", RestoreConfirmView.as_view(), name="restore-confirm"),
]
