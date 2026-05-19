from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import is_care_team_member
from apps.audit.services import record_audit_event
from apps.tasks.models import WorkflowTask
from apps.tasks.serializers import (
    WorkflowTaskAssignmentSerializer,
    WorkflowTaskSerializer,
    WorkflowTaskStatusSerializer,
)


def scoped_task_queryset(user, queryset):
    if user.role == User.Role.ADMIN:
        return queryset
    if user.role == User.Role.CHW:
        return queryset.filter(assigned_to_id=user.id)
    if user.facility_id:
        return queryset.filter(household__facility_id=user.facility_id) | queryset.filter(
            patient__facility_id=user.facility_id,
        )
    return queryset.none()


def can_manage_task(user, task: WorkflowTask) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.role == User.Role.ADMIN:
        return True
    if user.role == User.Role.CHW:
        return task.assigned_to_id == user.id
    return bool(
        user.facility_id
        and task.household
        and task.household.facility_id == user.facility_id,
    ) or bool(
        user.facility_id
        and task.patient
        and task.patient.facility_id == user.facility_id,
    )


@extend_schema_view(
    list=extend_schema(tags=["Tasks"], summary="List workflow tasks"),
    retrieve=extend_schema(tags=["Tasks"], summary="Retrieve workflow task"),
)
class WorkflowTaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WorkflowTask.objects.select_related(
        "patient",
        "household",
        "assigned_to",
        "household__facility",
    )
    serializer_class = WorkflowTaskSerializer

    def get_queryset(self):
        return scoped_task_queryset(self.request.user, self.queryset).distinct()

    @extend_schema(
        tags=["Tasks"],
        request=WorkflowTaskAssignmentSerializer,
        responses={200: WorkflowTaskSerializer},
        summary="Assign workflow task",
    )
    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        task = self.get_object()
        if not is_care_team_member(request.user):
            raise PermissionDenied("Only care-team users can assign workflow tasks.")

        serializer = WorkflowTaskAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assigned_to = serializer.validated_data["assigned_to"]

        facility_id = task.household.facility_id if task.household else task.patient.facility_id
        if assigned_to.facility_id != facility_id:
            raise ValidationError({"assigned_to": "Assigned CHW must belong to the same facility."})

        task.assigned_to = assigned_to
        task.save(update_fields=["assigned_to", "updated_at"])
        record_audit_event(request, "tasks.assign", "WorkflowTask", task.id)
        return Response(WorkflowTaskSerializer(task).data)

    @extend_schema(
        tags=["Tasks"],
        request=WorkflowTaskStatusSerializer,
        responses={200: WorkflowTaskSerializer},
        summary="Update workflow task status",
    )
    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        task = self.get_object()
        if not can_manage_task(request.user, task):
            raise PermissionDenied("You cannot update this workflow task.")

        serializer = WorkflowTaskStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task.status = serializer.validated_data["status"]
        task.completed_at = timezone.now() if task.status == WorkflowTask.Status.COMPLETED else None
        task.save(update_fields=["status", "completed_at", "updated_at"])
        record_audit_event(request, "tasks.update_status", "WorkflowTask", task.id)
        return Response(WorkflowTaskSerializer(task).data, status=status.HTTP_200_OK)
