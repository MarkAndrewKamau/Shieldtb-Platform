from rest_framework import serializers

from apps.patients.models import Patient


class PatientSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            "id",
            "external_id",
            "given_name",
            "family_name",
            "full_name",
            "date_of_birth",
            "sex",
            "phone",
            "national_id_hash",
            "facility",
            "enrollment_source",
            "consented_at",
            "consent_recorded_by",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "full_name", "consent_recorded_by", "created_at", "updated_at"]
        extra_kwargs = {
            "national_id_hash": {"write_only": True, "required": False},
        }

    def get_full_name(self, obj: Patient) -> str:
        return str(obj)
