from rest_framework import serializers

from apps.risk.models import RiskAssessment


class RiskAssessmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = RiskAssessment
        fields = [
            "id",
            "patient",
            "patient_name",
            "encounter",
            "score",
            "tier",
            "explanation",
            "model_version",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_patient_name(self, obj: RiskAssessment) -> str:
        return str(obj.patient)
