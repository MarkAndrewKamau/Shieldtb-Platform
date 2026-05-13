import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.audit.models import AuditEvent
from apps.clinical.models import ClinicalEncounter, ClinicalIntake
from apps.facilities.models import Facility
from apps.patients.models import Patient
from apps.risk.models import RiskAssessment


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


@pytest.fixture
def patient(facilities):
    facility, _other = facilities
    return Patient.objects.create(
        given_name="Amina",
        family_name="Otieno",
        sex=Patient.Sex.FEMALE,
        facility=facility,
    )


@pytest.mark.django_db
def test_create_intake_creates_encounter_intake_and_risk_assessment(clinician, patient):
    client = APIClient()
    client.force_authenticate(clinician)

    response = client.post(
        reverse("clinical-intake-list"),
        {
            "patient": patient.id,
            "occurred_at": timezone.now().isoformat(),
            "notes": "Initial ART clinic TB risk intake.",
            "cough": True,
            "hiv_positive": True,
            "household_tb_contact": True,
            "crowded_housing": True,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["encounter_type"] == ClinicalEncounter.EncounterType.INTAKE
    assert response.data["facility"] == patient.facility_id
    assert response.data["intake"]["has_who_tb_symptom"] is True
    assert response.data["risk_assessment"]["score"] == 90
    assert response.data["risk_assessment"]["tier"] == RiskAssessment.RiskTier.CRITICAL

    assert ClinicalEncounter.objects.count() == 1
    assert ClinicalIntake.objects.count() == 1
    assert RiskAssessment.objects.count() == 1
    assert AuditEvent.objects.filter(action="clinical.intake.create").exists()


@pytest.mark.django_db
def test_create_intake_rejects_cross_facility_patient(clinician, facilities):
    _facility, other = facilities
    other_patient = Patient.objects.create(
        given_name="Other",
        family_name="Patient",
        facility=other,
    )
    client = APIClient()
    client.force_authenticate(clinician)

    response = client.post(
        reverse("clinical-intake-list"),
        {
            "patient": other_patient.id,
            "occurred_at": timezone.now().isoformat(),
            "cough": True,
        },
        format="json",
    )

    assert response.status_code == 400
    assert ClinicalEncounter.objects.count() == 0
    assert RiskAssessment.objects.count() == 0
