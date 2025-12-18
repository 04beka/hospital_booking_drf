from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password, check_password

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)
        return self.create_user(email=email, password=password, **extra_fields)

class Gender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    OTHER = "O", "Other"

class RecoveryQuestion(models.TextChoices):
    DOG_NAME = "DOG_NAME", "What was your first dog's name?"
    FAV_CITY = "FAV_CITY", "What is your favorite city from childhood?"
    FAV_FOOD = "FAV_FOOD", "What is your favorite food?"

personal_id_validator = RegexValidator(
    regex=r"^\d{11}$",
    message="personal_id must be 11 digits"
)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    personal_id = models.CharField(max_length=11, unique=True, validators=[personal_id_validator])
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=Gender.choices)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    is_email_verified = models.BooleanField(default=False)

    recovery_question = models.CharField(max_length=32, choices=RecoveryQuestion.choices, blank=True)
    recovery_answer_hash = models.CharField(max_length=256, blank=True)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "personal_id", "birth_date", "gender"]

    def set_recovery_answer(self, answer: str) -> None:
        self.recovery_answer_hash = make_password(answer)

    def check_recovery_answer(self, answer: str) -> bool:
        if not self.recovery_answer_hash:
            return False
        return check_password(answer, self.recovery_answer_hash)

    def __str__(self):
        return self.email

class EmailVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verification_codes")
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    last_sent_at = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "code"]),
        ]

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at
