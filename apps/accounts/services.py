from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.core.signing import TimestampSigner

from .models import EmailVerificationCode, User
from .serializers import generate_6_digit_code

CODE_EXP_MINUTES = 20
RESEND_COOLDOWN_SECONDS = 60

def create_or_replace_code(user: User) -> EmailVerificationCode:
    code = generate_6_digit_code()
    now = timezone.now()
    expires = now + timedelta(minutes=CODE_EXP_MINUTES)

    obj = EmailVerificationCode.objects.create(
        user=user,
        code=code,
        expires_at=expires,
        is_used=False,
        last_sent_at=now
    )
    return obj

def can_resend(user: User) -> (bool, int):
    latest = EmailVerificationCode.objects.filter(user=user).order_by("-created_at").first()
    if not latest:
        return True, 0
    delta = (timezone.now() - latest.last_sent_at).total_seconds()
    if delta >= RESEND_COOLDOWN_SECONDS:
        return True, 0
    return False, int(RESEND_COOLDOWN_SECONDS - delta)

def send_verification_email(user: User, code: str) -> None:
    subject = "Verify your email"
    message = f"Your verification code is: {code}. It expires in {CODE_EXP_MINUTES} minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)

def make_recovery_token(user: User) -> str:
    signer = TimestampSigner()
    return signer.sign(user.pk)

def verify_recovery_token(token: str, max_age_seconds: int = 600) -> int:
    signer = TimestampSigner()
    value = signer.unsign(token, max_age=max_age_seconds)
    return int(value)
