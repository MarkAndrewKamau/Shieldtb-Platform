from django.contrib import admin

from apps.risk.models import RiskAssessment


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "score", "tier", "model_version", "created_at")
    list_filter = ("tier", "model_version")
    search_fields = ("patient__given_name", "patient__family_name")

