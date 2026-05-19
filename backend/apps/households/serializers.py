from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.permissions import is_care_team_member, user_can_access_facility
from apps.households.models import Household, HouseholdContact
from apps.households.services import ensure_household_screening_task
from apps.patients.models import Patient


class HouseholdContactWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseholdContact
        fields = [
            "patient",
            "full_name",
            "age_years",
            "phone",
            "relationship_to_index",
            "immunocompromised",
            "status",
        ]


class HouseholdContactSerializer(serializers.ModelSerializer):
    household_id = serializers.IntegerField(source="household.id", read_only=True)
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = HouseholdContact
        fields = [
            "id",
            "household",
            "household_id",
            "patient",
            "patient_name",
            "full_name",
            "age_years",
            "phone",
            "relationship_to_index",
            "immunocompromised",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "patient_name", "created_at", "updated_at"]

    def get_patient_name(self, obj: HouseholdContact) -> str:
        return str(obj.patient) if obj.patient else ""

    def validate(self, attrs):
        household = attrs.get("household") or getattr(self.instance, "household", None)
        patient = attrs.get("patient")
        request = self.context["request"]

        if household and not can_work_household(request.user, household):
            raise serializers.ValidationError("You cannot manage contacts for this household.")

        if patient and household and patient.facility_id != household.facility_id:
            raise serializers.ValidationError(
                {"patient": "Linked patient must belong to the same facility."},
            )

        return attrs


class HouseholdSerializer(serializers.ModelSerializer):
    facility = serializers.PrimaryKeyRelatedField(read_only=True)
    index_patient_name = serializers.SerializerMethodField()
    assigned_chw_name = serializers.SerializerMethodField()
    contacts = HouseholdContactSerializer(many=True, read_only=True)
    contact_entries = HouseholdContactWriteSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Household
        fields = [
            "id",
            "index_patient",
            "index_patient_name",
            "facility",
            "county",
            "sub_county",
            "ward",
            "village",
            "address_description",
            "latitude",
            "longitude",
            "assigned_chw",
            "assigned_chw_name",
            "contacts",
            "contact_entries",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "index_patient_name",
            "facility",
            "assigned_chw_name",
            "contacts",
            "created_at",
            "updated_at",
        ]

    def get_index_patient_name(self, obj: Household) -> str:
        return str(obj.index_patient)

    def get_assigned_chw_name(self, obj: Household) -> str:
        return str(obj.assigned_chw) if obj.assigned_chw else ""

    def validate_index_patient(self, patient: Patient) -> Patient:
        request = self.context["request"]
        if not user_can_access_facility(request.user, patient.facility_id):
            raise serializers.ValidationError("You cannot create a household for this patient.")
        return patient

    def validate_assigned_chw(self, user: User | None) -> User | None:
        if user is None:
            return user
        if user.role != User.Role.CHW:
            raise serializers.ValidationError("Assigned user must have the CHW role.")
        return user

    def validate(self, attrs):
        request = self.context["request"]
        index_patient = attrs.get("index_patient", getattr(self.instance, "index_patient", None))
        assigned_chw = attrs.get("assigned_chw", getattr(self.instance, "assigned_chw", None))

        if not is_care_team_member(request.user):
            raise serializers.ValidationError(
                "Only care-team users can create or update households.",
            )

        if assigned_chw and index_patient and assigned_chw.facility_id != index_patient.facility_id:
            raise serializers.ValidationError(
                {"assigned_chw": "Assigned CHW must belong to the same facility."},
            )

        if self.instance and "contact_entries" in attrs:
            raise serializers.ValidationError(
                {
                    "contact_entries": (
                        "Use the household contacts endpoint to add contacts after creation."
                    ),
                },
            )

        return attrs

    def create(self, validated_data):
        contact_entries = validated_data.pop("contact_entries", [])
        index_patient = validated_data["index_patient"]
        household = Household.objects.create(
            facility=index_patient.facility,
            **validated_data,
        )

        for entry in contact_entries:
            HouseholdContact.objects.create(household=household, **entry)

        ensure_household_screening_task(household)
        return household

    def update(self, instance, validated_data):
        validated_data.pop("contact_entries", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        ensure_household_screening_task(instance)
        return instance


def can_work_household(user, household: Household) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.role == User.Role.ADMIN:
        return True
    if user.role == User.Role.CHW:
        return household.assigned_chw_id == user.id
    return bool(user.facility_id and user.facility_id == household.facility_id)
