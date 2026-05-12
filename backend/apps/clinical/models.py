from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class ClinicalEncounter(TimeStampedModel):
    class EncounterType(models.TextChoices):
        INTAKE = "intake", "Intake"
        FOLLOW_UP = "follow_up", "Follow-up"
        HOUSEHOLD_SCREENING = "household_screening", "Household screening"
        ADR_REPORT = "adr_report", "ADR report"

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="encounters",
    )
    facility = models.ForeignKey("facilities.Facility", on_delete=models.PROTECT)
    encounter_type = models.CharField(max_length=32, choices=EncounterType.choices)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    occurred_at = models.DateTimeField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-occurred_at"]


class ClinicalIntake(TimeStampedModel):
    encounter = models.OneToOneField(
        ClinicalEncounter,
        on_delete=models.CASCADE,
        related_name="intake",
    )
    cough = models.BooleanField(default=False)
    fever = models.BooleanField(default=False)
    night_sweats = models.BooleanField(default=False)
    weight_loss = models.BooleanField(default=False)
    hiv_positive = models.BooleanField(default=False)
    pregnant = models.BooleanField(default=False)
    postpartum = models.BooleanField(default=False)
    diabetes = models.BooleanField(default=False)
    sle_or_autoimmune = models.BooleanField(default=False)
    ckd = models.BooleanField(default=False)
    on_immunosuppressants = models.BooleanField(default=False)
    previous_tb = models.BooleanField(default=False)
    household_tb_contact = models.BooleanField(default=False)
    crowded_housing = models.BooleanField(default=False)
    poor_ventilation = models.BooleanField(default=False)
    medication_history = models.JSONField(default=dict, blank=True)

    @property
    def has_who_tb_symptom(self) -> bool:
        return self.cough or self.fever or self.night_sweats or self.weight_loss
