from django.db import models

from apps.core.models import TimeStampedModel


class Household(TimeStampedModel):
    index_patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="indexed_households",
    )
    facility = models.ForeignKey("facilities.Facility", on_delete=models.PROTECT)
    county = models.CharField(max_length=100, blank=True)
    sub_county = models.CharField(max_length=100, blank=True)
    ward = models.CharField(max_length=100, blank=True)
    village = models.CharField(max_length=100, blank=True)
    address_description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    assigned_chw = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_households",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Household {self.pk} for {self.index_patient}"


class HouseholdContact(TimeStampedModel):
    class ScreeningStatus(models.TextChoices):
        PENDING = "pending", "Pending screening"
        SCREENED = "screened", "Screened"
        REFERRED = "referred", "Referred"
        STARTED_TPT = "started_tpt", "Started TPT"
        MISSED_FOLLOW_UP = "missed_follow_up", "Missed follow-up"
        COMPLETED = "completed", "Completed"

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="contacts")
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="household_contact_records",
    )
    full_name = models.CharField(max_length=255)
    age_years = models.PositiveSmallIntegerField(null=True, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    relationship_to_index = models.CharField(max_length=100, blank=True)
    immunocompromised = models.BooleanField(default=False)
    status = models.CharField(
        max_length=32,
        choices=ScreeningStatus.choices,
        default=ScreeningStatus.PENDING,
    )

    class Meta:
        ordering = ["status", "full_name"]

    def __str__(self) -> str:
        return self.full_name

