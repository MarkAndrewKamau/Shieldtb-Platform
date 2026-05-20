import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.facilities.models import Facility
from apps.households.models import Household
from apps.notifications.models import Notification
from apps.patients.models import Patient
from apps.tasks.models import WorkflowTask


@pytest.fixture
def notification_entities(db):
    facility = Facility.objects.create(
        name="Kibera Dispensary",
        code="KE-NBO-KIB-001",
        facility_type=Facility.FacilityType.DISPENSARY,
    )
    other_facility = Facility.objects.create(
        name="Mbagathi Hospital",
        code="KE-NBO-MBA-001",
        facility_type=Facility.FacilityType.HOSPITAL,
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
    other_chw = User.objects.create_user(
        username="otherchw",
        password="password",
        role=User.Role.CHW,
        facility=other_facility,
    )
    patient = Patient.objects.create(
        given_name="Index",
        family_name="Patient",
        facility=facility,
    )
    household = Household.objects.create(index_patient=patient, facility=facility, assigned_chw=chw)
    task = WorkflowTask.objects.create(
        task_type=WorkflowTask.TaskType.HOUSEHOLD_SCREENING,
        patient=patient,
        household=household,
        assigned_to=chw,
        title="Screen household for Index Patient",
    )
    own_notification = Notification.objects.create(
        patient=patient,
        recipient_user=chw,
        workflow_task=task,
        channel=Notification.Channel.IN_APP,
        status=Notification.Status.DELIVERED,
        recipient=chw.username,
        template_key="workflow_task.assignment",
        payload={"task_id": task.id},
    )
    other_notification = Notification.objects.create(
        recipient_user=other_chw,
        channel=Notification.Channel.IN_APP,
        status=Notification.Status.DELIVERED,
        recipient=other_chw.username,
        template_key="workflow_task.assignment",
        payload={},
    )
    return clinician, chw, other_chw, patient, own_notification, other_notification


@pytest.mark.django_db
def test_household_creation_with_assigned_chw_creates_in_app_notification():
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
    client = APIClient()
    client.force_authenticate(clinician)

    response = client.post(
        reverse("household-list"),
        {
            "index_patient": patient.id,
            "assigned_chw": chw.id,
            "county": "Nairobi",
            "contact_entries": [
                {
                    "full_name": "Mary Otieno",
                    "status": "pending",
                }
            ],
        },
        format="json",
    )

    assert response.status_code == 201
    notification = Notification.objects.get(template_key="workflow_task.assignment")
    assert notification.recipient_user == chw
    assert notification.workflow_task is not None
    assert notification.channel == Notification.Channel.IN_APP
    assert notification.status == Notification.Status.DELIVERED


@pytest.mark.django_db
def test_repeated_household_update_with_same_assignee_does_not_duplicate_assignment_notification():
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
    Notification.objects.create(
        patient=patient,
        recipient_user=chw,
        workflow_task=task,
        channel=Notification.Channel.IN_APP,
        status=Notification.Status.DELIVERED,
        recipient=chw.username,
        template_key="workflow_task.assignment",
        payload={"task_id": task.id},
    )
    client = APIClient()
    client.force_authenticate(clinician)

    response = client.patch(
        reverse("household-detail", args=[household.id]),
        {"address_description": "Updated landmark"},
        format="json",
    )

    assert response.status_code == 200
    assert Notification.objects.filter(template_key="workflow_task.assignment").count() == 1


@pytest.mark.django_db
def test_chw_only_lists_own_notifications(notification_entities):
    (
        _clinician,
        chw,
        _other_chw,
        _patient,
        own_notification,
        _other_notification,
    ) = notification_entities
    client = APIClient()
    client.force_authenticate(chw)

    response = client.get(reverse("notification-list"))

    assert response.status_code == 200
    assert [item["id"] for item in response.data] == [own_notification.id]


@pytest.mark.django_db
def test_clinician_can_list_facility_notifications(notification_entities):
    (
        clinician,
        _chw,
        _other_chw,
        _patient,
        own_notification,
        _other_notification,
    ) = notification_entities
    client = APIClient()
    client.force_authenticate(clinician)

    response = client.get(reverse("notification-list"))

    assert response.status_code == 200
    assert [item["id"] for item in response.data] == [own_notification.id]
