import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.audit.models import AuditEvent
from apps.facilities.models import Facility
from apps.patients.models import Patient


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
def clinician(facilities):
    facility, _other = facilities
    return User.objects.create_user(
        username="clinician",
        password="password",
        role=User.Role.CLINICIAN,
        facility=facility,
    )


@pytest.mark.django_db
def test_clinician_can_create_patient_for_own_facility(clinician, facilities):
    facility, _other = facilities
    client = APIClient()
    client.force_authenticate(clinician)

    response = client.post(
        reverse("patient-list"),
        {
            "external_id": "P-001",
            "given_name": "Amina",
            "family_name": "Otieno",
            "sex": Patient.Sex.FEMALE,
            "phone": "+254700000001",
            "national_id_hash": "hashed-national-id",
            "facility": facility.id,
            "enrollment_source": Patient.EnrollmentSource.ART_CLINIC,
            "consented_at": timezone.now().isoformat(),
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["full_name"] == "Amina Otieno"
    assert "national_id_hash" not in response.data

    patient = Patient.objects.get(external_id="P-001")
    assert patient.facility == facility
    assert patient.consent_recorded_by == clinician
    assert AuditEvent.objects.filter(action="patients.create", resource_id=str(patient.id)).exists()


@pytest.mark.django_db
def test_clinician_cannot_create_patient_for_other_facility(clinician, facilities):
    _facility, other = facilities
    client = APIClient()
    client.force_authenticate(clinician)

    response = client.post(
        reverse("patient-list"),
        {
            "given_name": "Blocked",
            "family_name": "Patient",
            "sex": Patient.Sex.UNKNOWN,
            "facility": other.id,
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_clinician_only_lists_patients_in_own_facility(clinician, facilities):
    facility, other = facilities
    own_patient = Patient.objects.create(
        given_name="Own",
        family_name="Patient",
        facility=facility,
    )
    Patient.objects.create(
        given_name="Other",
        family_name="Patient",
        facility=other,
    )
    client = APIClient()
    client.force_authenticate(clinician)

    response = client.get(reverse("patient-list"))

    assert response.status_code == 200
    assert [patient["id"] for patient in response.data] == [own_patient.id]
