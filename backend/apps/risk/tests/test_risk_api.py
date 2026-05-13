import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.clinical.models import ClinicalEncounter
from apps.facilities.models import Facility
from apps.patients.models import Patient
from apps.risk.models import RiskAssessment


@pytest.mark.django_db
def test_risk_assessment_list_is_facility_scoped():
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
    own_patient = Patient.objects.create(
        given_name="Own",
        family_name="Patient",
        facility=own_facility,
    )
    other_patient = Patient.objects.create(
        given_name="Other",
        family_name="Patient",
        facility=other_facility,
    )
    own_encounter = ClinicalEncounter.objects.create(
        patient=own_patient,
        facility=own_facility,
        encounter_type=ClinicalEncounter.EncounterType.INTAKE,
        recorded_by=clinician,
        occurred_at=timezone.now(),
    )
    other_encounter = ClinicalEncounter.objects.create(
        patient=other_patient,
        facility=other_facility,
        encounter_type=ClinicalEncounter.EncounterType.INTAKE,
        recorded_by=clinician,
        occurred_at=timezone.now(),
    )
    own_risk = RiskAssessment.objects.create(
        patient=own_patient,
        encounter=own_encounter,
        score=55,
        tier=RiskAssessment.RiskTier.HIGH,
    )
    RiskAssessment.objects.create(
        patient=other_patient,
        encounter=other_encounter,
        score=80,
        tier=RiskAssessment.RiskTier.CRITICAL,
    )
    client = APIClient()
    client.force_authenticate(clinician)

    response = client.get("/api/v1/risk-assessments/")

    assert response.status_code == 200
    assert [risk["id"] for risk in response.data] == [own_risk.id]
