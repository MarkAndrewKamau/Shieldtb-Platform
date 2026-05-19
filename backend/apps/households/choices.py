from django.db import models


class HouseholdContactScreeningStatus(models.TextChoices):
    PENDING = "pending", "Pending screening"
    SCREENED = "screened", "Screened"
    REFERRED = "referred", "Referred"
    STARTED_TPT = "started_tpt", "Started TPT"
    MISSED_FOLLOW_UP = "missed_follow_up", "Missed follow-up"
    COMPLETED = "completed", "Completed"
