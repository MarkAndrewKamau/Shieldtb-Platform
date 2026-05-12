from django.contrib import admin

from apps.audit.models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "resource_type", "resource_id", "created_at")
    list_filter = ("action", "resource_type")
    search_fields = ("resource_type", "resource_id", "actor__username")
    readonly_fields = ("created_at", "updated_at")

