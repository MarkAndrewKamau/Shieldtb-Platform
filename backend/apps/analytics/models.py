from django.db import models

from apps.core.models import TimeStampedModel


class FacilityDailyMetric(TimeStampedModel):
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.CASCADE,
        related_name="daily_metrics",
    )
    date = models.DateField()
    patients_enrolled = models.PositiveIntegerField(default=0)
    high_risk_patients = models.PositiveIntegerField(default=0)
    contacts_pending_screening = models.PositiveIntegerField(default=0)
    contacts_screened = models.PositiveIntegerField(default=0)
    tpt_started = models.PositiveIntegerField(default=0)
    missed_follow_ups = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["facility", "date"], name="unique_facility_metric_day")
        ]
        ordering = ["-date", "facility__name"]

