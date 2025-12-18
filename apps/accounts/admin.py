from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User, EmailVerificationCode

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ("email","first_name","last_name","personal_id","is_email_verified","is_staff","is_active")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email","password")}),
        ("Personal info", {"fields": ("first_name","last_name","personal_id","birth_date","gender")}),
        ("Recovery", {"fields": ("recovery_question","recovery_answer_hash")}),
        ("Permissions", {"fields": ("is_active","is_staff","is_superuser","groups","user_permissions")}),
        ("Verification", {"fields": ("is_email_verified",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email","password1","password2","first_name","last_name","personal_id","birth_date","gender","is_staff","is_superuser"),
        }),
    )
    search_fields = ("email","personal_id")
    readonly_fields = ("recovery_answer_hash",)

@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ("user","code","expires_at","is_used","last_sent_at","created_at")
    search_fields = ("user__email","code")
