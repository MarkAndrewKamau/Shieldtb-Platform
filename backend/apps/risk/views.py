from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.risk.models import RiskAssessment
from apps.risk.serializers import RiskAssessmentSerializer


class RiskAssessmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RiskAssessmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = RiskAssessment.objects.select_related(
            "patient",
            "encounter",
            "patient__facility",
        )
        if self.request.user.role == "admin":
            return queryset
        if self.request.user.facility_id:
            return queryset.filter(patient__facility_id=self.request.user.facility_id)
        return queryset.none()
