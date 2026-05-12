from django.contrib import admin

from apps.patients.models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "given_name",
        "family_name",
        "sex",
        "facility",
        "enrollment_source",
        "is_active",
    )
    list_filter = ("sex", "facility", "enrollment_source", "is_active")
    search_fields = ("given_name", "family_name", "external_id", "phone")
