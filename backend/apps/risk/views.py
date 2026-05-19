from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.risk.models import RiskAssessment
from apps.risk.serializers import RiskAssessmentSerializer


@extend_schema_view(
    list=extend_schema(tags=["Risk"], summary="List risk assessments"),
    retrieve=extend_schema(tags=["Risk"], summary="Retrieve risk assessment"),
)
class RiskAssessmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RiskAssessment.objects.select_related(
        "patient",
        "encounter",
        "patient__facility",
    )
    serializer_class = RiskAssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "admin":
            return self.queryset
        if self.request.user.facility_id:
            return self.queryset.filter(patient__facility_id=self.request.user.facility_id)
        return self.queryset.none()
