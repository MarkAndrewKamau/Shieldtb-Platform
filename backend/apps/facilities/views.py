from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from apps.accounts.permissions import IsAdminOrReadOnly
from apps.audit.services import record_audit_event
from apps.facilities.models import Facility
from apps.facilities.serializers import FacilitySerializer


@extend_schema_view(
    list=extend_schema(tags=["Facilities"], summary="List facilities"),
    retrieve=extend_schema(tags=["Facilities"], summary="Retrieve facility"),
    create=extend_schema(tags=["Facilities"], summary="Create facility"),
    update=extend_schema(tags=["Facilities"], summary="Update facility"),
    partial_update=extend_schema(tags=["Facilities"], summary="Partially update facility"),
    destroy=extend_schema(tags=["Facilities"], summary="Delete facility"),
)
class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Facility.objects.all()
        if self.request.user.role == "admin":
            return queryset
        if self.request.user.facility_id:
            return queryset.filter(id=self.request.user.facility_id)
        return queryset.none()

    def perform_create(self, serializer):
        facility = serializer.save()
        record_audit_event(self.request, "facilities.create", "Facility", facility.id)

    def perform_update(self, serializer):
        facility = serializer.save()
        record_audit_event(self.request, "facilities.update", "Facility", facility.id)
