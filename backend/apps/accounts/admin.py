from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import User


@admin.register(User)
class ShieldTBUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("ShieldTB", {"fields": ("role", "facility", "phone", "must_reset_password")}),
    )
    list_display = ("username", "email", "role", "facility", "is_active", "is_staff")
    list_filter = ("role", "facility", "is_active", "is_staff")

