from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Patient(TimeStampedModel):
    class Sex(models.TextChoices):
        FEMALE = "female", "Female"
        MALE = "male", "Male"
        INTERSEX = "intersex", "Intersex"
        UNKNOWN = "unknown", "Unknown"

    class EnrollmentSource(models.TextChoices):
        ART_CLINIC = "art_clinic", "ART clinic"
        ANC = "anc", "Antenatal care"
        DISPENSARY = "dispensary", "Dispensary"
        COMMUNITY = "community", "Community"
        SELF_REFERRAL = "self_referral", "Self-referral"
        LAB = "lab", "Laboratory"

    external_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    given_name = models.CharField(max_length=150)
    family_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=16, choices=Sex.choices, default=Sex.UNKNOWN)
    phone = models.CharField(max_length=32, blank=True)
    national_id_hash = models.CharField(max_length=128, blank=True)
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.PROTECT,
        related_name="patients",
    )
    enrollment_source = models.CharField(
        max_length=32,
        choices=EnrollmentSource.choices,
        default=EnrollmentSource.DISPENSARY,
    )
    consented_at = models.DateTimeField(null=True, blank=True)
    consent_recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_consents_recorded",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["family_name", "given_name"]

    def __str__(self) -> str:
        return f"{self.given_name} {self.family_name}"

