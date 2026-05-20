from django.db.models import Q
from django.utils import timezone

from apps.notifications.choices import NotificationChannel, NotificationStatus
from apps.notifications.models import Notification
from apps.notifications.providers import ConsoleNotificationProvider, InAppNotificationProvider

TASK_ASSIGNMENT_TEMPLATE = "workflow_task.assignment"


def provider_for_channel(channel: str):
    if channel == NotificationChannel.IN_APP:
        return InAppNotificationProvider()
    return ConsoleNotificationProvider()


def dispatch_notification(notification: Notification) -> Notification:
    if notification.status == Notification.Status.CANCELLED:
        return notification

    if notification.scheduled_for and notification.scheduled_for > timezone.now():
        return notification

    provider = provider_for_channel(notification.channel)
    try:
        result = provider.send(notification)
    except Exception as exc:  # pragma: no cover - defensive catch for adapter failures
        notification.status = NotificationStatus.FAILED
        notification.failure_reason = str(exc)[:255]
        notification.save(update_fields=["status", "failure_reason", "updated_at"])
        return notification

    notification.status = result.status
    notification.provider_message_id = result.provider_message_id
    notification.failure_reason = result.failure_reason
    notification.sent_at = timezone.now()
    notification.save(
        update_fields=[
            "status",
            "provider_message_id",
            "failure_reason",
            "sent_at",
            "updated_at",
        ],
    )
    return notification


def create_notification(
    *,
    channel: str,
    recipient: str,
    template_key: str,
    **kwargs,
) -> Notification:
    notification = Notification.objects.create(
        channel=channel,
        recipient=recipient,
        template_key=template_key,
        **kwargs,
    )
    return dispatch_notification(notification)


def notify_workflow_task_assignment(task) -> Notification | None:
    if not task.assigned_to:
        return None

    assignee = task.assigned_to
    recipient = assignee.username
    payload = {
        "task_id": task.id,
        "task_type": task.task_type,
        "task_title": task.title,
        "patient_id": task.patient_id,
        "household_id": task.household_id,
        "facility_id": assignee.facility_id,
    }
    return create_notification(
        patient=task.patient,
        recipient_user=assignee,
        workflow_task=task,
        channel=NotificationChannel.IN_APP,
        recipient=recipient,
        template_key=TASK_ASSIGNMENT_TEMPLATE,
        payload=payload,
    )


def scoped_notification_queryset(user, queryset):
    if user.role == "admin":
        return queryset
    if user.role == "chw":
        return queryset.filter(recipient_user_id=user.id)
    if user.facility_id:
        return queryset.filter(
            Q(patient__facility_id=user.facility_id)
            | Q(recipient_user__facility_id=user.facility_id),
        )
    return queryset.none()
