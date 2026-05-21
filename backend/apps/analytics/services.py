from django.db.models import Q
from django.utils import timezone

from apps.analytics.models import FacilityDailyMetric
from apps.facilities.models import Facility
from apps.households.models import Household, HouseholdContact
from apps.notifications.models import Notification
from apps.patients.models import Patient
from apps.risk.models import RiskAssessment
from apps.tasks.models import WorkflowTask


def latest_risk_assessments_for_facility(facility: Facility):
    return (
        RiskAssessment.objects.filter(patient__facility=facility)
        .order_by("patient_id", "-created_at")
        .distinct("patient_id")
    )


def scoped_analytics_facilities(user):
    queryset = Facility.objects.all()
    if user.role in {"admin", "analyst"}:
        return queryset
    if user.facility_id:
        return queryset.filter(id=user.facility_id)
    return queryset.none()


def compute_facility_summary(facility: Facility, *, summary_date=None) -> dict:
    summary_date = summary_date or timezone.localdate()

    latest_risks = latest_risk_assessments_for_facility(facility)
    high_risk_tiers = [RiskAssessment.RiskTier.HIGH, RiskAssessment.RiskTier.CRITICAL]
    active_task_qs = WorkflowTask.objects.filter(
        Q(household__facility=facility) | Q(patient__facility=facility),
    ).distinct()
    notification_qs = Notification.objects.filter(
        Q(patient__facility=facility) | Q(recipient_user__facility=facility),
    ).distinct()

    return {
        "facility_id": facility.id,
        "facility_name": facility.name,
        "facility_code": facility.code,
        "facility_type": facility.facility_type,
        "summary_date": summary_date,
        "active_patients": Patient.objects.filter(facility=facility, is_active=True).count(),
        "patients_enrolled_today": Patient.objects.filter(
            facility=facility,
            created_at__date=summary_date,
        ).count(),
        "high_risk_patients": latest_risks.filter(tier__in=high_risk_tiers).count(),
        "moderate_or_higher_risk_patients": latest_risks.exclude(
            tier=RiskAssessment.RiskTier.LOW,
        ).count(),
        "households_tracked": Household.objects.filter(facility=facility).count(),
        "contacts_pending_screening": HouseholdContact.objects.filter(
            household__facility=facility,
            status=HouseholdContact.ScreeningStatus.PENDING,
        ).count(),
        "contacts_screened": HouseholdContact.objects.filter(
            household__facility=facility,
            status=HouseholdContact.ScreeningStatus.SCREENED,
        ).count(),
        "tpt_started": HouseholdContact.objects.filter(
            household__facility=facility,
            status=HouseholdContact.ScreeningStatus.STARTED_TPT,
        ).count(),
        "missed_follow_ups": HouseholdContact.objects.filter(
            household__facility=facility,
            status=HouseholdContact.ScreeningStatus.MISSED_FOLLOW_UP,
        ).count(),
        "open_workflow_tasks": active_task_qs.exclude(
            status__in=[WorkflowTask.Status.COMPLETED, WorkflowTask.Status.CANCELLED],
        ).count(),
        "completed_tasks_today": active_task_qs.filter(completed_at__date=summary_date).count(),
        "notifications_sent_today": notification_qs.filter(sent_at__date=summary_date).count(),
    }


def refresh_facility_daily_metric(facility: Facility) -> FacilityDailyMetric:
    today = timezone.localdate()
    summary = compute_facility_summary(facility, summary_date=today)

    metric, _created = FacilityDailyMetric.objects.update_or_create(
        facility=facility,
        date=today,
        defaults={
            "patients_enrolled": summary["patients_enrolled_today"],
            "high_risk_patients": summary["high_risk_patients"],
            "contacts_pending_screening": summary["contacts_pending_screening"],
            "contacts_screened": summary["contacts_screened"],
            "tpt_started": summary["tpt_started"],
            "missed_follow_ups": summary["missed_follow_ups"],
        },
    )
    return metric
