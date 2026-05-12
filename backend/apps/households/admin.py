from django.contrib import admin

from apps.households.models import Household, HouseholdContact


class HouseholdContactInline(admin.TabularInline):
    model = HouseholdContact
    extra = 0


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    inlines = [HouseholdContactInline]
    list_display = ("index_patient", "facility", "ward", "village", "assigned_chw", "created_at")
    list_filter = ("facility", "county", "sub_county", "ward")
    search_fields = ("index_patient__given_name", "index_patient__family_name", "village")

