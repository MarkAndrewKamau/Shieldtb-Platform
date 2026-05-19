from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from apps.accounts.models import User
from apps.accounts.permissions import is_care_team_member
from apps.audit.services import record_audit_event
from apps.households.models import Household, HouseholdContact
from apps.households.serializers import (
    HouseholdContactSerializer,
    HouseholdSerializer,
    can_work_household,
)


def scoped_household_queryset(user, queryset):
    if user.role == User.Role.ADMIN:
        return queryset
    if user.role == User.Role.CHW:
        return queryset.filter(assigned_chw_id=user.id)
    if user.facility_id:
        return queryset.filter(facility_id=user.facility_id)
    return queryset.none()


def scoped_contact_queryset(user, queryset):
    if user.role == User.Role.ADMIN:
        return queryset
    if user.role == User.Role.CHW:
        return queryset.filter(household__assigned_chw_id=user.id)
    if user.facility_id:
        return queryset.filter(household__facility_id=user.facility_id)
    return queryset.none()


@extend_schema_view(
    list=extend_schema(tags=["Households"], summary="List households"),
    retrieve=extend_schema(tags=["Households"], summary="Retrieve household"),
    create=extend_schema(tags=["Households"], summary="Create household trace"),
    update=extend_schema(tags=["Households"], summary="Update household"),
    partial_update=extend_schema(tags=["Households"], summary="Partially update household"),
    destroy=extend_schema(tags=["Households"], summary="Delete household"),
)
class HouseholdViewSet(viewsets.ModelViewSet):
    queryset = (
        Household.objects.select_related("index_patient", "facility", "assigned_chw")
        .prefetch_related("contacts")
    )
    serializer_class = HouseholdSerializer

    def get_queryset(self):
        return scoped_household_queryset(self.request.user, self.queryset)

    def perform_create(self, serializer):
        if not is_care_team_member(self.request.user):
            raise PermissionDenied("Only care-team users can create households.")
        household = serializer.save()
        record_audit_event(self.request, "households.create", "Household", household.id)

    def perform_update(self, serializer):
        if not is_care_team_member(self.request.user):
            raise PermissionDenied("Only care-team users can update households.")
        household = serializer.save()
        record_audit_event(self.request, "households.update", "Household", household.id)


@extend_schema_view(
    list=extend_schema(tags=["Households"], summary="List household contacts"),
    retrieve=extend_schema(tags=["Households"], summary="Retrieve household contact"),
    create=extend_schema(tags=["Households"], summary="Create household contact"),
    update=extend_schema(tags=["Households"], summary="Update household contact"),
    partial_update=extend_schema(tags=["Households"], summary="Partially update household contact"),
    destroy=extend_schema(tags=["Households"], summary="Delete household contact"),
)
class HouseholdContactViewSet(viewsets.ModelViewSet):
    queryset = HouseholdContact.objects.select_related(
        "household",
        "patient",
        "household__assigned_chw",
    )
    serializer_class = HouseholdContactSerializer

    def get_queryset(self):
        return scoped_contact_queryset(self.request.user, self.queryset)

    def perform_create(self, serializer):
        household = serializer.validated_data["household"]
        if not can_work_household(self.request.user, household):
            raise PermissionDenied("You cannot add contacts to this household.")
        contact = serializer.save()
        record_audit_event(
            self.request,
            "households.contacts.create",
            "HouseholdContact",
            contact.id,
        )

    def perform_update(self, serializer):
        household = serializer.instance.household
        if not can_work_household(self.request.user, household):
            raise PermissionDenied("You cannot update contacts for this household.")
        contact = serializer.save()
        record_audit_event(
            self.request,
            "households.contacts.update",
            "HouseholdContact",
            contact.id,
        )
