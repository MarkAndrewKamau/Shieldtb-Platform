from rest_framework import serializers

from apps.analytics.models import FacilityDailyMetric


class FacilitySummarySerializer(serializers.Serializer):
    facility_id = serializers.IntegerField()
    facility_name = serializers.CharField()
    facility_code = serializers.CharField()
    facility_type = serializers.CharField()
    summary_date = serializers.DateField()
    active_patients = serializers.IntegerField()
    patients_enrolled_today = serializers.IntegerField()
    high_risk_patients = serializers.IntegerField()
    moderate_or_higher_risk_patients = serializers.IntegerField()
    households_tracked = serializers.IntegerField()
    contacts_pending_screening = serializers.IntegerField()
    contacts_screened = serializers.IntegerField()
    tpt_started = serializers.IntegerField()
    missed_follow_ups = serializers.IntegerField()
    open_workflow_tasks = serializers.IntegerField()
    completed_tasks_today = serializers.IntegerField()
    notifications_sent_today = serializers.IntegerField()


class FacilityDailyMetricSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source="facility.name", read_only=True)
    facility_code = serializers.CharField(source="facility.code", read_only=True)

    class Meta:
        model = FacilityDailyMetric
        fields = [
            "id",
            "facility",
            "facility_name",
            "facility_code",
            "date",
            "patients_enrolled",
            "high_risk_patients",
            "contacts_pending_screening",
            "contacts_screened",
            "tpt_started",
            "missed_follow_ups",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class RefreshFacilityMetricsSerializer(serializers.Serializer):
    facility = serializers.IntegerField(required=False, min_value=1)
