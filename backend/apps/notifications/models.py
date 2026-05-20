from django.db import models

from apps.core.models import TimeStampedModel
from apps.notifications.choices import NotificationChannel, NotificationStatus


class Notification(TimeStampedModel):
    Channel = NotificationChannel
    Status = NotificationStatus

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    recipient_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    workflow_task = models.ForeignKey(
        "tasks.WorkflowTask",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    channel = models.CharField(max_length=24, choices=NotificationChannel.choices)
    status = models.CharField(
        max_length=24,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
    )
    recipient = models.CharField(max_length=100)
    template_key = models.CharField(max_length=100)
    payload = models.JSONField(default=dict, blank=True)
    provider_message_id = models.CharField(max_length=150, blank=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["status", "scheduled_for", "-created_at"]

    def __str__(self) -> str:
        return f"{self.template_key} -> {self.recipient}"
