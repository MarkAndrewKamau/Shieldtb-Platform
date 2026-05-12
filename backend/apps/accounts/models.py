from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        CLINICIAN = "clinician", "Clinician"
        CHW = "chw", "Community health worker"
        FACILITY_OFFICER = "facility_officer", "Facility officer"
        ANALYST = "analyst", "Analyst"

    role = models.CharField(max_length=32, choices=Role.choices, default=Role.CHW)
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    phone = models.CharField(max_length=32, blank=True)
    must_reset_password = models.BooleanField(default=False)


class AccessTokenBlocklist(models.Model):
    jti = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revoked_access_tokens",
    )
    reason = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.jti

    @classmethod
    def is_blocked(cls, jti: str) -> bool:
        return cls.objects.filter(jti=jti, expires_at__gt=timezone.now()).exists()
