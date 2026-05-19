import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.audit.models import AuditEvent
from apps.facilities.models import Facility
from apps.households.models import Household, HouseholdContact
from apps.patients.models import Patient
from apps.tasks.models import WorkflowTask


@pytest.fixture
def facilities(db):
    first = Facility.objects.create(
        name="Kibera Dispensary",
        code="KE-NBO-KIB-001",
        facility_type=Facility.FacilityType.DISPENSARY,
    )
    second = Facility.objects.create(
        name="Mbagathi Hospital",
        code="KE-NBO-MBA-001",
        facility_type=Facility.FacilityType.HOSPITAL,
    )
    return first, second


@pytest.fixture
def users(facilities):
    own_facility, other_facility = facilities
    clinician = User.objects.create_user(
        username="clinician",
        password="password",
        role=User.Role.CLINICIAN,
        facility=own_facility,
    )
    chw = User.objects.create_user(
        username="chw",
        password="password",
        role=User.Role.CHW,
        facility=own_facility,
    )
    other_chw = User.objects.create_user(
        username="otherchw",
        password="password",
        role=User.Role.CHW,
        facility=other_facility,
    )
    return clinician, chw, other_chw


@pytest.fixture
def patients(facilities):
    own_facility, other_facility = facilities
    own_patient = Patient.objects.create(
        given_name="Index",
        family_name="Patient",
        facility=own_facility,
    )
    other_patient = Patient.objects.create(
        given_name="Other",
        family_name="Patient",
        facility=other_facility,
    )
    return own_patient, other_patient


@pytest.mark.django_db
def test_clinician_can_create_household_with_contacts_and_screening_task(users, patients):
    clinician, chw, _other_chw = users
    own_patient, _other_patient = patients
    client = APIClient()
    client.force_authenticate(clinician)

    response = client.post(
        reverse("household-list"),
        {
            "index_patient": own_patient.id,
            "assigned_chw": chw.id,
            "county": "Nairobi",
            "sub_county": "Kibra",
            "ward": "Laini Saba",
            "village": "Village A",
            "address_description": "Near the community hall.",
            "contact_entries": [
                {
                    "full_name": "Mary Otieno",
                    "age_years": 34,
                    "phone": "+254700000301",
                    "relationship_to_index": "Spouse",
                    "immunocompromised": False,
                    "status": "pending",
                },
                {
                    "full_name": "Kevin Otieno",
                    "age_years": 6,
                    "relationship_to_index": "Child",
                    "immunocompromised": True,
                    "status": "pending",
                },
            ],
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["facility"] == own_patient.facility_id
    assert len(response.data["contacts"]) == 2
    assert Household.objects.count() == 1
    assert HouseholdContact.objects.count() == 2

    task = WorkflowTask.objects.get(task_type=WorkflowTask.TaskType.HOUSEHOLD_SCREENING)
    assert task.household.index_patient == own_patient
    assert task.assigned_to == chw
    assert task.metadata["contact_count"] == 2
    assert AuditEvent.objects.filter(action="households.create").exists()


@pytest.mark.django_db
def test_chw_only_lists_assigned_households(users, patients):
    clinician, chw, other_chw = users
    own_patient, _other_patient = patients
    own_household = Household.objects.create(
        index_patient=own_patient,
        facility=own_patient.facility,
        assigned_chw=chw,
    )
    Household.objects.create(
        index_patient=own_patient,
        facility=own_patient.facility,
        assigned_chw=other_chw,
    )
    client = APIClient()
    client.force_authenticate(chw)

    response = client.get(reverse("household-list"))

    assert response.status_code == 200
    assert [household["id"] for household in response.data] == [own_household.id]


@pytest.mark.django_db
def test_clinician_cannot_create_household_for_other_facility_patient(users, patients):
    clinician, _chw, _other_chw = users
    _own_patient, other_patient = patients
    client = APIClient()
    client.force_authenticate(clinician)

    response = client.post(
        reverse("household-list"),
        {
            "index_patient": other_patient.id,
            "county": "Nairobi",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_chw_can_update_contact_status_for_assigned_household(users, patients):
    clinician, chw, _other_chw = users
    own_patient, _other_patient = patients
    household = Household.objects.create(
        index_patient=own_patient,
        facility=own_patient.facility,
        assigned_chw=chw,
    )
    contact = HouseholdContact.objects.create(
        household=household,
        full_name="Mary Otieno",
    )
    client = APIClient()
    client.force_authenticate(chw)

    response = client.patch(
        reverse("household-contact-detail", args=[contact.id]),
        {"status": HouseholdContact.ScreeningStatus.SCREENED},
        format="json",
    )

    assert response.status_code == 200
    contact.refresh_from_db()
    assert contact.status == HouseholdContact.ScreeningStatus.SCREENED
    assert AuditEvent.objects.filter(action="households.contacts.update").exists()
