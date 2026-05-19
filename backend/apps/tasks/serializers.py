from rest_framework import serializers

from apps.accounts.models import User
from apps.tasks.models import WorkflowTask


class WorkflowTaskSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    household_id = serializers.IntegerField(source="household.id", read_only=True)
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowTask
        fields = [
            "id",
            "task_type",
            "status",
            "patient",
            "patient_name",
            "household",
            "household_id",
            "assigned_to",
            "assigned_to_name",
            "due_at",
            "completed_at",
            "title",
            "description",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_patient_name(self, obj: WorkflowTask) -> str:
        return str(obj.patient) if obj.patient else ""

    def get_assigned_to_name(self, obj: WorkflowTask) -> str:
        return str(obj.assigned_to) if obj.assigned_to else ""


class WorkflowTaskAssignmentSerializer(serializers.Serializer):
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def validate_assigned_to(self, user: User) -> User:
        if user.role != User.Role.CHW:
            raise serializers.ValidationError("Workflow tasks can only be assigned to CHW users.")
        return user


class WorkflowTaskStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=WorkflowTask.Status.choices)
