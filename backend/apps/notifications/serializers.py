from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    recipient_user_name = serializers.SerializerMethodField()
    workflow_task_title = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "patient",
            "patient_name",
            "recipient_user",
            "recipient_user_name",
            "workflow_task",
            "workflow_task_title",
            "channel",
            "status",
            "recipient",
            "template_key",
            "payload",
            "provider_message_id",
            "failure_reason",
            "scheduled_for",
            "sent_at",
            "read_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_patient_name(self, obj: Notification) -> str:
        return str(obj.patient) if obj.patient else ""

    def get_recipient_user_name(self, obj: Notification) -> str:
        return str(obj.recipient_user) if obj.recipient_user else ""

    def get_workflow_task_title(self, obj: Notification) -> str:
        return obj.workflow_task.title if obj.workflow_task else ""
