from django.contrib import admin

from apps.tasks.models import WorkflowTask


@admin.register(WorkflowTask)
class WorkflowTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "task_type", "status", "assigned_to", "due_at")
    list_filter = ("task_type", "status", "assigned_to")
    search_fields = ("title", "patient__given_name", "patient__family_name")

