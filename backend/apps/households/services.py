from apps.notifications.services import notify_workflow_task_assignment
from apps.tasks.models import WorkflowTask


def ensure_household_screening_task(household):
    task = (
        WorkflowTask.objects.filter(
            household=household,
            task_type=WorkflowTask.TaskType.HOUSEHOLD_SCREENING,
        )
        .exclude(status__in=[WorkflowTask.Status.COMPLETED, WorkflowTask.Status.CANCELLED])
        .first()
    )

    if task:
        previous_assignee_id = task.assigned_to_id
        contact_count = household.contacts.count()
        task.assigned_to = household.assigned_chw
        task.patient = household.index_patient
        task.title = f"Screen household for {household.index_patient}"
        task.metadata = {
            **task.metadata,
            "contact_count": contact_count,
            "household_id": household.id,
        }
        task.save(
            update_fields=[
                "assigned_to",
                "patient",
                "title",
                "metadata",
                "updated_at",
            ],
        )
        if task.assigned_to_id and task.assigned_to_id != previous_assignee_id:
            notify_workflow_task_assignment(task)
        return task

    task = WorkflowTask.objects.create(
        task_type=WorkflowTask.TaskType.HOUSEHOLD_SCREENING,
        status=WorkflowTask.Status.OPEN,
        patient=household.index_patient,
        household=household,
        assigned_to=household.assigned_chw,
        title=f"Screen household for {household.index_patient}",
        description="Complete household contact screening and update contact statuses.",
        metadata={
            "contact_count": household.contacts.count(),
            "household_id": household.id,
        },
    )
    if task.assigned_to_id:
        notify_workflow_task_assignment(task)
    return task
