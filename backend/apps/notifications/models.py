from django.db import models

from apps.core.models import TimeStampedModel


class Notification(TimeStampedModel):
    class Channel(models.TextChoices):
        SMS = "sms", "SMS"
        WHATSAPP = "whatsapp", "WhatsApp"
        USSD = "ussd", "USSD"
        IN_APP = "in_app", "In-app"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    channel = models.CharField(max_length=24, choices=Channel.choices)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING)
    recipient = models.CharField(max_length=100)
    template_key = models.CharField(max_length=100)
    payload = models.JSONField(default=dict, blank=True)
    provider_message_id = models.CharField(max_length=150, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["status", "scheduled_for", "-created_at"]

