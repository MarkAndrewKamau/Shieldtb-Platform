import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.analytics.models import FacilityDailyMetric
from apps.clinical.models import ClinicalEncounter
from apps.facilities.models import Facility
from apps.households.models import Household, HouseholdContact
from apps.notifications.models import Notification
from apps.patients.models import Patient
from apps.risk.models import RiskAssessment
from apps.tasks.models import WorkflowTask


@pytest.fixture
def analytics_entities(db):
    own_facility = Facility.objects.create(
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
        facility=own_facility,
    )
    analyst = User.objects.create_user(
        username="analyst",
        password="password",
        role=User.Role.ANALYST,
    )
    chw = User.objects.create_user(
        username="chw",
        password="password",
        role=User.Role.CHW,
        facility=own_facility,
    )
    own_patient = Patient.objects.create(
        given_name="Amina",
        family_name="Otieno",
        facility=own_facility,
        is_active=True,
    )
    Patient.objects.create(
        given_name="Other",
        family_name="Patient",
        facility=other_facility,
        is_active=True,
    )
    own_encounter = ClinicalEncounter.objects.create(
        patient=own_patient,
        facility=own_facility,
        encounter_type=ClinicalEncounter.EncounterType.INTAKE,
        recorded_by=clinician,
        occurred_at=timezone.now(),
    )
    RiskAssessment.objects.create(
        patient=own_patient,
        encounter=own_encounter,
        score=70,
        tier=RiskAssessment.RiskTier.HIGH,
    )
    household = Household.objects.create(
        index_patient=own_patient,
        facility=own_facility,
        assigned_chw=chw,
    )
    HouseholdContact.objects.create(
        household=household,
        full_name="Pending Contact",
        status=HouseholdContact.ScreeningStatus.PENDING,
    )
    HouseholdContact.objects.create(
        household=household,
        full_name="Screened Contact",
        status=HouseholdContact.ScreeningStatus.SCREENED,
    )
    task = WorkflowTask.objects.create(
        task_type=WorkflowTask.TaskType.HOUSEHOLD_SCREENING,
        status=WorkflowTask.Status.OPEN,
        patient=own_patient,
        household=household,
        assigned_to=chw,
        title="Screen household for Amina Otieno",
    )
    Notification.objects.create(
        patient=own_patient,
        recipient_user=chw,
        workflow_task=task,
        channel=Notification.Channel.IN_APP,
        status=Notification.Status.DELIVERED,
        recipient=chw.username,
        template_key="workflow_task.assignment",
        sent_at=timezone.now(),
    )
    return {
        "own_facility": own_facility,
        "other_facility": other_facility,
        "clinician": clinician,
        "analyst": analyst,
        "chw": chw,
    }


@pytest.mark.django_db
def test_facility_summary_is_facility_scoped(analytics_entities):
    client = APIClient()
    client.force_authenticate(analytics_entities["clinician"])

    response = client.get(reverse("facility-summary-list"))

    assert response.status_code == 200
    assert len(response.data) == 1
    summary = response.data[0]
    assert summary["facility_id"] == analytics_entities["own_facility"].id
    assert summary["active_patients"] == 1
    assert summary["high_risk_patients"] == 1
    assert summary["contacts_pending_screening"] == 1
    assert summary["contacts_screened"] == 1
    assert summary["open_workflow_tasks"] == 1
    assert summary["notifications_sent_today"] == 1


@pytest.mark.django_db
def test_admin_or_analyst_refresh_can_create_daily_metric_snapshot(analytics_entities):
    client = APIClient()
    client.force_authenticate(analytics_entities["analyst"])

    response = client.post(
        reverse("facility-daily-metric-refresh"),
        {"facility": analytics_entities["own_facility"].id},
        format="json",
    )

    assert response.status_code == 200
    metric = FacilityDailyMetric.objects.get(facility=analytics_entities["own_facility"])
    assert metric.high_risk_patients == 1
    assert metric.contacts_pending_screening == 1
    assert metric.contacts_screened == 1


@pytest.mark.django_db
def test_non_admin_non_analyst_cannot_refresh_daily_metrics(analytics_entities):
    client = APIClient()
    client.force_authenticate(analytics_entities["clinician"])

    response = client.post(reverse("facility-daily-metric-refresh"), {}, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_daily_metrics_list_is_facility_scoped(analytics_entities):
    own_facility = analytics_entities["own_facility"]
    other_facility = analytics_entities["other_facility"]
    today = timezone.localdate()
    own_metric = FacilityDailyMetric.objects.create(
        facility=own_facility,
        date=today,
        patients_enrolled=1,
    )
    FacilityDailyMetric.objects.create(
        facility=other_facility,
        date=today,
        patients_enrolled=1,
    )
    client = APIClient()
    client.force_authenticate(analytics_entities["chw"])

    response = client.get(reverse("facility-daily-metric-list"))

    assert response.status_code == 200
    assert [item["id"] for item in response.data] == [own_metric.id]
