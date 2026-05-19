from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import scoped_facility_queryset
from apps.audit.services import record_audit_event
from apps.clinical.models import ClinicalEncounter
from apps.clinical.serializers import ClinicalEncounterSerializer, IntakeCreateSerializer


@extend_schema_view(
    list=extend_schema(tags=["Clinical"], summary="List clinical encounters"),
    retrieve=extend_schema(tags=["Clinical"], summary="Retrieve clinical encounter"),
)
class ClinicalEncounterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClinicalEncounter.objects.select_related(
        "patient",
        "facility",
        "recorded_by",
        "intake",
        "risk_assessment",
    )
    serializer_class = ClinicalEncounterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return scoped_facility_queryset(self.request.user, self.queryset)


@extend_schema_view(
    create=extend_schema(tags=["Clinical"], summary="Create structured intake"),
)
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
