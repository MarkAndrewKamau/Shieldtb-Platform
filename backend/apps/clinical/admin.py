from django.contrib import admin

from apps.clinical.models import ClinicalEncounter, ClinicalIntake


class ClinicalIntakeInline(admin.StackedInline):
    model = ClinicalIntake
    extra = 0


@admin.register(ClinicalEncounter)
class ClinicalEncounterAdmin(admin.ModelAdmin):
    inlines = [ClinicalIntakeInline]
    list_display = ("patient", "facility", "encounter_type", "recorded_by", "occurred_at")
    list_filter = ("encounter_type", "facility")
    search_fields = ("patient__given_name", "patient__family_name")

