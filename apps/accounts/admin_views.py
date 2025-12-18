from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","email","first_name","last_name","personal_id","birth_date","gender","is_email_verified","is_active","is_staff"]

class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-id")
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
