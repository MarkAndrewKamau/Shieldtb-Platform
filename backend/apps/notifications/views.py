from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer
from apps.notifications.services import scoped_notification_queryset


@extend_schema_view(
    list=extend_schema(tags=["Notifications"], summary="List notifications"),
    retrieve=extend_schema(tags=["Notifications"], summary="Retrieve notification"),
)
class NotificationViewSet(ReadOnlyModelViewSet):
    queryset = Notification.objects.select_related("patient", "recipient_user", "workflow_task")
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return scoped_notification_queryset(self.request.user, self.queryset)

    @extend_schema(
        tags=["Notifications"],
        responses={200: NotificationSerializer},
        summary="Mark notification read",
    )
    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        if not notification.read_at:
            notification.read_at = timezone.now()
            notification.save(update_fields=["read_at", "updated_at"])
        return Response(NotificationSerializer(notification).data)
