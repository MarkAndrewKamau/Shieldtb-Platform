from rest_framework import viewsets

from apps.accounts.permissions import IsAdminOrReadOnly
from apps.audit.services import record_audit_event
from apps.facilities.models import Facility
from apps.facilities.serializers import FacilitySerializer


class FacilityViewSet(viewsets.ModelViewSet):
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
