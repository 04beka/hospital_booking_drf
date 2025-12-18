from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import EmailVerificationCode
from .serializers import (
    RegisterSerializer, VerifyEmailSerializer, ResendCodeSerializer,
    RecoveryVerifySerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from .services import (
    create_or_replace_code, can_resend, send_verification_email,
    make_recovery_token, verify_recovery_token
)

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()

        code_obj = create_or_replace_code(user)
        send_verification_email(user, code_obj.code)

        return Response({
            "message": "Registered. Verification code sent to email.",
            "email": user.email
        }, status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = VerifyEmailSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"]
        code = ser.validated_data["code"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)

        code_obj = EmailVerificationCode.objects.filter(
            user=user, code=code, is_used=False
        ).order_by("-created_at").first()

        if not code_obj:
            return Response({"detail": "Invalid code"}, status=400)
        if code_obj.is_expired():
            return Response({"detail": "Code expired"}, status=400)

        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
        code_obj.is_used = True
        code_obj.save(update_fields=["is_used"])

        return Response({"message": "Email verified"}, status=200)

class ResendCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = ResendCodeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)

        if user.is_email_verified:
            return Response({"detail": "Email already verified"}, status=400)

        ok, wait_seconds = can_resend(user)
        if not ok:
            return Response({"detail": f"Cooldown active. Try again in {wait_seconds}s"}, status=429)

        code_obj = create_or_replace_code(user)
        send_verification_email(user, code_obj.code)

        return Response({"message": "Verification code resent"}, status=200)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        if not user.is_email_verified:
            raise Exception("Email is not verified")
        return data

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RecoveryVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RecoveryVerifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.validated_data["user"]
        token = make_recovery_token(user)
        return Response({"recovery_token": token}, status=200)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = PasswordResetRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        email = ser.validated_data["email"]
        recovery_token = ser.validated_data["recovery_token"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)

        # Require recovery token (covers the exam requirement)
        try:
            user_id = verify_recovery_token(recovery_token, max_age_seconds=600)
        except Exception:
            return Response({"detail": "Invalid or expired recovery token"}, status=400)
        if user_id != user.pk:
            return Response({"detail": "Recovery token does not match user"}, status=400)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)

        reset_link = f"{settings.FRONTEND_BASE_URL}/api/auth/password-reset/confirm/?uid={uid}&token={token}"

        # Send email
        from django.core.mail import send_mail
        send_mail(
            subject="Password reset",
            message=f"Use this link to reset your password: {reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        # For exam/demo convenience, also return link
        return Response({"message": "Password reset link sent to email.", "reset_link": reset_link}, status=200)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = PasswordResetConfirmSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        uidb64 = ser.validated_data["uid"]
        token = ser.validated_data["token"]
        new_password = ser.validated_data["new_password"]

        try:
            uid = int(force_str(urlsafe_base64_decode(uidb64)))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"detail": "Invalid uid"}, status=400)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({"detail": "Invalid or expired token"}, status=400)

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response({"message": "Password updated"}, status=200)
