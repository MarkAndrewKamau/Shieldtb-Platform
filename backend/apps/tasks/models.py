from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.tasks.choices import WorkflowTaskStatus, WorkflowTaskType


class WorkflowTask(TimeStampedModel):
    TaskType = WorkflowTaskType
    Status = WorkflowTaskStatus

    task_type = models.CharField(max_length=40, choices=WorkflowTaskType.choices)
    status = models.CharField(
        max_length=32,
        choices=WorkflowTaskStatus.choices,
        default=WorkflowTaskStatus.OPEN,
    )
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
