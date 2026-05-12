from django.contrib.auth.models import AbstractUser
from django.db import models


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

