from django.contrib import admin

from apps.facilities.models import Facility


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "facility_type", "county", "sub_county", "is_active")
    list_filter = ("facility_type", "county", "is_active")
    search_fields = ("name", "code", "county", "sub_county", "ward")

