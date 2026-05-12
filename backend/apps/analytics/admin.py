from django.contrib import admin

from apps.analytics.models import FacilityDailyMetric


@admin.register(FacilityDailyMetric)
class FacilityDailyMetricAdmin(admin.ModelAdmin):
    list_display = (
        "facility",
        "date",
        "patients_enrolled",
        "high_risk_patients",
        "contacts_pending_screening",
        "contacts_screened",
        "tpt_started",
        "missed_follow_ups",
    )
    list_filter = ("facility", "date")

