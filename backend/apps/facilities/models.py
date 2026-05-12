from django.db import models

from apps.core.models import TimeStampedModel


class Facility(TimeStampedModel):
    class FacilityType(models.TextChoices):
        DISPENSARY = "dispensary", "Dispensary"
        HEALTH_CENTRE = "health_centre", "Health centre"
        HOSPITAL = "hospital", "Hospital"
        LAB = "lab", "Laboratory"
        COMMUNITY_UNIT = "community_unit", "Community unit"

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64, unique=True)
    facility_type = models.CharField(max_length=32, choices=FacilityType.choices)
    county = models.CharField(max_length=100, blank=True)
    sub_county = models.CharField(max_length=100, blank=True)
    ward = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "facilities"

    def __str__(self) -> str:
        return self.name

