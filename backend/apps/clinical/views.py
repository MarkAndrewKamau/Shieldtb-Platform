from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import scoped_facility_queryset
from apps.audit.services import record_audit_event
from apps.clinical.models import ClinicalEncounter
from apps.clinical.serializers import ClinicalEncounterSerializer, IntakeCreateSerializer


class ClinicalEncounterViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ClinicalEncounterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ClinicalEncounter.objects.select_related(
            "patient",
            "facility",
            "recorded_by",
            "intake",
            "risk_assessment",
        )
        return scoped_facility_queryset(self.request.user, queryset)


class IntakeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = IntakeCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        encounter = serializer.save()
        record_audit_event(request, "clinical.intake.create", "ClinicalEncounter", encounter.id)
        return Response(
            ClinicalEncounterSerializer(encounter, context={"request": request}).data,
            status=201,
        )
