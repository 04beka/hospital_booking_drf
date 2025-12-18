from django.utils import timezone
from django.conf import settings
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from .models import User, EmailVerificationCode, RecoveryQuestion

def generate_6_digit_code() -> str:
    import random
    return f"{random.randint(0, 999999):06d}"

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    recovery_question = serializers.ChoiceField(choices=RecoveryQuestion.choices)
    recovery_answer = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email","password","first_name","last_name","personal_id","birth_date","gender",
                  "recovery_question","recovery_answer"]

    def validate_password(self, value):
        # no custom rules requested; keep Django default validators
        validate_password(value)
        return value

    def create(self, validated_data):
        recovery_answer = validated_data.pop("recovery_answer")
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        user.set_recovery_answer(recovery_answer)
        user.is_email_verified = False
        user.save(update_fields=["recovery_answer_hash","is_email_verified"])
        return user

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)

class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

class RecoveryVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    recovery_question = serializers.ChoiceField(choices=RecoveryQuestion.choices)
    recovery_answer = serializers.CharField()

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found"})
        if user.recovery_question != attrs["recovery_question"]:
            raise serializers.ValidationError({"recovery_question": "Incorrect recovery question"})
        if not user.check_recovery_answer(attrs["recovery_answer"]):
            raise serializers.ValidationError({"recovery_answer": "Incorrect answer"})
        attrs["user"] = user
        return attrs

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    recovery_token = serializers.CharField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        validate_password(value)
        return value
