from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.risk.models import RiskAssessment
from apps.risk.serializers import RiskAssessmentSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Risk"],
        summary="List risk assessments",
        parameters=[
            OpenApiParameter(
                name="patient",
                description="Filter risk assessments by patient ID.",
                required=False,
                type=int,
            )
        ],
    ),
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
            queryset = self.queryset
        elif self.request.user.facility_id:
            queryset = self.queryset.filter(patient__facility_id=self.request.user.facility_id)
        else:
            queryset = self.queryset.none()

        patient_id = self.request.query_params.get("patient")
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset
