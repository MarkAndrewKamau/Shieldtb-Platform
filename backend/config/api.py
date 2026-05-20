from rest_framework.routers import DefaultRouter

from apps.accounts.views import UserViewSet
from apps.clinical.views import ClinicalEncounterViewSet, IntakeViewSet
from apps.facilities.views import FacilityViewSet
from apps.households.views import HouseholdContactViewSet, HouseholdViewSet
from apps.notifications.views import NotificationViewSet
from apps.patients.views import PatientViewSet
from apps.risk.views import RiskAssessmentViewSet
from apps.tasks.views import WorkflowTaskViewSet

router = DefaultRouter()
router.register("facilities", FacilityViewSet, basename="facility")
router.register("users", UserViewSet, basename="user")
router.register("patients", PatientViewSet, basename="patient")
router.register("households", HouseholdViewSet, basename="household")
router.register("household-contacts", HouseholdContactViewSet, basename="household-contact")
router.register("notifications", NotificationViewSet, basename="notification")
router.register("clinical/encounters", ClinicalEncounterViewSet, basename="clinical-encounter")
router.register("clinical/intakes", IntakeViewSet, basename="clinical-intake")
router.register("risk-assessments", RiskAssessmentViewSet, basename="risk-assessment")
router.register("workflow-tasks", WorkflowTaskViewSet, basename="workflow-task")
