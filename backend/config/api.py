from rest_framework.routers import DefaultRouter

from apps.accounts.views import UserViewSet
from apps.clinical.views import ClinicalEncounterViewSet, IntakeViewSet
from apps.facilities.views import FacilityViewSet
from apps.patients.views import PatientViewSet
from apps.risk.views import RiskAssessmentViewSet

router = DefaultRouter()
router.register("facilities", FacilityViewSet, basename="facility")
router.register("users", UserViewSet, basename="user")
router.register("patients", PatientViewSet, basename="patient")
router.register("clinical/encounters", ClinicalEncounterViewSet, basename="clinical-encounter")
router.register("clinical/intakes", IntakeViewSet, basename="clinical-intake")
router.register("risk-assessments", RiskAssessmentViewSet, basename="risk-assessment")
