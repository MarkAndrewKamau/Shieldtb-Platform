import logging
import uuid
from dataclasses import dataclass

from apps.notifications.choices import NotificationStatus
from apps.notifications.models import Notification

logger = logging.getLogger(__name__)


@dataclass
class DeliveryResult:
    status: str
    provider_message_id: str
    failure_reason: str = ""


class NotificationProvider:
    def send(self, notification: Notification) -> DeliveryResult:
        raise NotImplementedError


class InAppNotificationProvider(NotificationProvider):
    def send(self, notification: Notification) -> DeliveryResult:
        provider_message_id = f"inapp-{uuid.uuid4()}"
        return DeliveryResult(
            status=NotificationStatus.DELIVERED,
            provider_message_id=provider_message_id,
        )


class ConsoleNotificationProvider(NotificationProvider):
    def send(self, notification: Notification) -> DeliveryResult:
        provider_message_id = f"console-{uuid.uuid4()}"
        logger.info(
            "Dispatching %s notification to %s with template %s",
            notification.channel,
            notification.recipient,
            notification.template_key,
        )
        return DeliveryResult(
            status=NotificationStatus.SENT,
            provider_message_id=provider_message_id,
        )
