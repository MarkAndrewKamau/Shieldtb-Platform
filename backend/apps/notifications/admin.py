from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "channel", "template_key", "status", "scheduled_for", "sent_at")
    list_filter = ("channel", "status", "template_key")
    search_fields = ("recipient", "provider_message_id")

