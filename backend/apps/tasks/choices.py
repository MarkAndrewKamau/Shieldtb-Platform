from django.db import models


class WorkflowTaskType(models.TextChoices):
    HOUSEHOLD_SCREENING = "household_screening", "Household screening"
    PATIENT_FOLLOW_UP = "patient_follow_up", "Patient follow-up"
    POSTPARTUM_CHECK_IN = "postpartum_check_in", "Postpartum check-in"
    ADR_TRIAGE = "adr_triage", "ADR triage"
    TPT_ELIGIBILITY_REVIEW = "tpt_eligibility_review", "TPT eligibility review"


class WorkflowTaskStatus(models.TextChoices):
    OPEN = "open", "Open"
    IN_PROGRESS = "in_progress", "In progress"
    BLOCKED = "blocked", "Blocked"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
