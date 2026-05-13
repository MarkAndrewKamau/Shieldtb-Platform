from django.db import transaction
from rest_framework import serializers

from apps.accounts.permissions import user_can_access_facility
from apps.clinical.models import ClinicalEncounter, ClinicalIntake
from apps.patients.models import Patient
from apps.risk.serializers import RiskAssessmentSerializer
from apps.risk.services import RuleBasedRiskScorer


class ClinicalIntakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalIntake
        fields = [
            "id",
            "cough",
            "fever",
            "night_sweats",
            "weight_loss",
            "hiv_positive",
            "pregnant",
            "postpartum",
            "diabetes",
            "sle_or_autoimmune",
            "ckd",
            "on_immunosuppressants",
            "previous_tb",
            "household_tb_contact",
            "crowded_housing",
            "poor_ventilation",
            "medication_history",
            "has_who_tb_symptom",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "has_who_tb_symptom", "created_at", "updated_at"]


class ClinicalEncounterSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    intake = ClinicalIntakeSerializer(read_only=True)
    risk_assessment = RiskAssessmentSerializer(read_only=True)

    class Meta:
        model = ClinicalEncounter
        fields = [
            "id",
            "patient",
            "patient_name",
            "facility",
            "encounter_type",
            "recorded_by",
            "occurred_at",
            "notes",
            "intake",
            "risk_assessment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "patient_name",
            "facility",
            "recorded_by",
            "intake",
            "risk_assessment",
            "created_at",
            "updated_at",
        ]

    def get_patient_name(self, obj: ClinicalEncounter) -> str:
        return str(obj.patient)


class IntakeCreateSerializer(serializers.Serializer):
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.select_related("facility"),
    )
    occurred_at = serializers.DateTimeField()
    notes = serializers.CharField(required=False, allow_blank=True)
    cough = serializers.BooleanField(default=False)
    fever = serializers.BooleanField(default=False)
    night_sweats = serializers.BooleanField(default=False)
    weight_loss = serializers.BooleanField(default=False)
    hiv_positive = serializers.BooleanField(default=False)
    pregnant = serializers.BooleanField(default=False)
    postpartum = serializers.BooleanField(default=False)
    diabetes = serializers.BooleanField(default=False)
    sle_or_autoimmune = serializers.BooleanField(default=False)
    ckd = serializers.BooleanField(default=False)
    on_immunosuppressants = serializers.BooleanField(default=False)
    previous_tb = serializers.BooleanField(default=False)
    household_tb_contact = serializers.BooleanField(default=False)
    crowded_housing = serializers.BooleanField(default=False)
    poor_ventilation = serializers.BooleanField(default=False)
    medication_history = serializers.JSONField(required=False)

    def validate_patient(self, patient: Patient) -> Patient:
        request = self.context["request"]
        if not user_can_access_facility(request.user, patient.facility_id):
            raise serializers.ValidationError("You cannot create intake for this patient.")
        if not patient.is_active:
            raise serializers.ValidationError("Cannot create intake for an inactive patient.")
        return patient

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        patient = validated_data.pop("patient")
        occurred_at = validated_data.pop("occurred_at")
        notes = validated_data.pop("notes", "")

        encounter = ClinicalEncounter.objects.create(
            patient=patient,
            facility=patient.facility,
            encounter_type=ClinicalEncounter.EncounterType.INTAKE,
            recorded_by=request.user,
            occurred_at=occurred_at,
            notes=notes,
        )
        intake = ClinicalIntake.objects.create(encounter=encounter, **validated_data)
        RuleBasedRiskScorer().create_assessment(intake)
        return encounter
