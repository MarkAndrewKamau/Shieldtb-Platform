from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class WorkflowTask(TimeStampedModel):
    class TaskType(models.TextChoices):
        HOUSEHOLD_SCREENING = "household_screening", "Household screening"
        PATIENT_FOLLOW_UP = "patient_follow_up", "Patient follow-up"
        POSTPARTUM_CHECK_IN = "postpartum_check_in", "Postpartum check-in"
        ADR_TRIAGE = "adr_triage", "ADR triage"
        TPT_ELIGIBILITY_REVIEW = "tpt_eligibility_review", "TPT eligibility review"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        BLOCKED = "blocked", "Blocked"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    task_type = models.CharField(max_length=40, choices=TaskType.choices)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.OPEN)
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="workflow_tasks",
    )
    household = models.ForeignKey(
        "households.Household",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="workflow_tasks",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    due_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["status", "due_at", "-created_at"]

    def __str__(self) -> str:
        return self.title

