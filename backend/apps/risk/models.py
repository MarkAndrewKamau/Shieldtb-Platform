from django.db import models

from apps.core.models import TimeStampedModel


class RiskAssessment(TimeStampedModel):
    class RiskTier(models.TextChoices):
        LOW = "low", "Low"
        MODERATE = "moderate", "Moderate"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="risk_assessments",
    )
    encounter = models.OneToOneField(
        "clinical.ClinicalEncounter",
        on_delete=models.CASCADE,
        related_name="risk_assessment",
    )
    score = models.PositiveSmallIntegerField()
    tier = models.CharField(max_length=16, choices=RiskTier.choices)
    explanation = models.JSONField(default=dict, blank=True)
    model_version = models.CharField(max_length=64, default="rules-v0")

    class Meta:
        ordering = ["-created_at"]

