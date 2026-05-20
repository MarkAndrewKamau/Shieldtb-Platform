import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.audit.models import AuditEvent
from apps.facilities.models import Facility
from apps.households.models import Household
from apps.notifications.models import Notification
from apps.patients.models import Patient
from apps.tasks.models import WorkflowTask


@pytest.fixture
def setup_entities(db):
    facility = Facility.objects.create(
        name="Kibera Dispensary",
        code="KE-NBO-KIB-001",
        facility_type=Facility.FacilityType.DISPENSARY,
    )
    clinician = User.objects.create_user(
        username="clinician",
        password="password",
        role=User.Role.CLINICIAN,
        facility=facility,
    )
    chw = User.objects.create_user(
        username="chw",
        password="password",
        role=User.Role.CHW,
        facility=facility,
    )
    patient = Patient.objects.create(
        given_name="Index",
        family_name="Patient",
        facility=facility,
    )
    household = Household.objects.create(
        index_patient=patient,
        facility=facility,
        assigned_chw=chw,
    )
    task = WorkflowTask.objects.create(
        task_type=WorkflowTask.TaskType.HOUSEHOLD_SCREENING,
        patient=patient,
        household=household,
        assigned_to=chw,
        title="Screen household for Index Patient",
    )
    return clinician, chw, household, task


@pytest.mark.django_db
def test_chw_only_lists_assigned_workflow_tasks(setup_entities):
    _clinician, chw, _household, task = setup_entities
    client = APIClient()
    client.force_authenticate(chw)

    response = client.get(reverse("workflow-task-list"))

    assert response.status_code == 200
    assert [item["id"] for item in response.data] == [task.id]


@pytest.mark.django_db
def test_clinician_can_assign_household_screening_task_to_chw(setup_entities):
    clinician, chw, _household, task = setup_entities
    task.assigned_to = None
    task.save(update_fields=["assigned_to", "updated_at"])
    client = APIClient()
    client.force_authenticate(clinician)

    response = client.post(
        reverse("workflow-task-assign", args=[task.id]),
        {"assigned_to": chw.id},
        format="json",
    )

    assert response.status_code == 200
    task.refresh_from_db()
    assert task.assigned_to == chw
    notification = Notification.objects.get(template_key="workflow_task.assignment")
    assert notification.recipient_user == chw
    assert notification.workflow_task == task
    assert AuditEvent.objects.filter(action="tasks.assign").exists()


@pytest.mark.django_db
def test_chw_can_update_own_task_status(setup_entities):
    _clinician, chw, _household, task = setup_entities
    client = APIClient()
    client.force_authenticate(chw)

    response = client.post(
        reverse("workflow-task-update-status", args=[task.id]),
        {"status": WorkflowTask.Status.COMPLETED},
        format="json",
    )

    assert response.status_code == 200
    task.refresh_from_db()
    assert task.status == WorkflowTask.Status.COMPLETED
    assert task.completed_at is not None
    assert AuditEvent.objects.filter(action="tasks.update_status").exists()
