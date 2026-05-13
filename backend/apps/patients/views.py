from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.permissions import scoped_facility_queryset, user_can_access_facility
from apps.audit.services import record_audit_event
from apps.patients.models import Patient
from apps.patients.serializers import PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer

    def get_queryset(self):
        queryset = Patient.objects.select_related("facility", "consent_recorded_by")
        return scoped_facility_queryset(self.request.user, queryset)

    def perform_create(self, serializer):
        facility = serializer.validated_data.get("facility")
        if not facility:
            raise ValidationError({"facility": "This field is required."})
        if not user_can_access_facility(self.request.user, facility.id):
            raise PermissionDenied("You cannot create patients for this facility.")

        consented_at = serializer.validated_data.get("consented_at")
        patient = serializer.save(
            consent_recorded_by=self.request.user if consented_at else None,
        )
        record_audit_event(self.request, "patients.create", "Patient", patient.id)

    def perform_update(self, serializer):
        facility = serializer.validated_data.get("facility", serializer.instance.facility)
        if not user_can_access_facility(self.request.user, facility.id):
            raise PermissionDenied("You cannot update patients for this facility.")

        consent_recorded_by = serializer.instance.consent_recorded_by
        if serializer.validated_data.get("consented_at") and not consent_recorded_by:
            consent_recorded_by = self.request.user

        patient = serializer.save(consent_recorded_by=consent_recorded_by)
        record_audit_event(self.request, "patients.update", "Patient", patient.id)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.updated_at = timezone.now()
        instance.save(update_fields=["is_active", "updated_at"])
        record_audit_event(self.request, "patients.deactivate", "Patient", instance.id)
