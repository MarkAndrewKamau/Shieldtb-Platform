from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
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
