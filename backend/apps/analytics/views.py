from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.analytics.models import FacilityDailyMetric
from apps.analytics.serializers import (
    FacilityDailyMetricSerializer,
    FacilitySummarySerializer,
    RefreshFacilityMetricsSerializer,
)
from apps.analytics.services import (
    compute_facility_summary,
    refresh_facility_daily_metric,
    scoped_analytics_facilities,
)
from apps.facilities.models import Facility


def can_refresh_analytics(user) -> bool:
    return bool(user and user.is_authenticated and user.role in {"admin", "analyst"})


@extend_schema_view(
    list=extend_schema(
        tags=["Analytics"],
        summary="List facility summaries",
        responses={200: FacilitySummarySerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Analytics"],
        summary="Retrieve facility summary",
        responses={200: FacilitySummarySerializer},
    ),
)
class FacilitySummaryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FacilitySummarySerializer
    queryset = Facility.objects.all()

    def list(self, request):
        facilities = scoped_analytics_facilities(request.user)
        summaries = [compute_facility_summary(facility) for facility in facilities]
        return Response(FacilitySummarySerializer(summaries, many=True).data)

    def retrieve(self, request, pk=None):
        facility = scoped_analytics_facilities(request.user).filter(pk=pk).first()
        if not facility:
            raise NotFound("Facility summary not found.")
        summary = compute_facility_summary(facility)
        return Response(FacilitySummarySerializer(summary).data)


@extend_schema_view(
    list=extend_schema(tags=["Analytics"], summary="List daily facility metrics"),
    retrieve=extend_schema(tags=["Analytics"], summary="Retrieve daily facility metric"),
)
class FacilityDailyMetricViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FacilityDailyMetric.objects.select_related("facility")
    serializer_class = FacilityDailyMetricSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        facilities = scoped_analytics_facilities(self.request.user)
        queryset = self.queryset.filter(facility__in=facilities)
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        return queryset

    @extend_schema(
        tags=["Analytics"],
        request=RefreshFacilityMetricsSerializer,
        responses={200: FacilityDailyMetricSerializer(many=True)},
        summary="Refresh today's daily facility metrics",
    )
    @action(detail=False, methods=["post"])
    def refresh(self, request):
        if not can_refresh_analytics(request.user):
            raise PermissionDenied("Only admin or analyst users can refresh analytics.")

        serializer = RefreshFacilityMetricsSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        facility_id = serializer.validated_data.get("facility")

        facilities = scoped_analytics_facilities(request.user)
        if facility_id:
            facilities = facilities.filter(id=facility_id)

        metrics = [refresh_facility_daily_metric(facility) for facility in facilities]
        response_serializer = FacilityDailyMetricSerializer(metrics, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
