from django.core.management.base import BaseCommand, CommandError

from apps.analytics.services import refresh_facility_daily_metric
from apps.facilities.models import Facility


class Command(BaseCommand):
    help = "Refresh today's facility daily metrics snapshots."

    def add_arguments(self, parser):
        parser.add_argument(
            "--facility-id",
            type=int,
            help="Refresh metrics for one facility only.",
        )

    def handle(self, *args, **options):
        facility_id = options.get("facility_id")
        facilities = Facility.objects.all()

        if facility_id:
            facilities = facilities.filter(id=facility_id)
            if not facilities.exists():
                raise CommandError(f"Facility {facility_id} does not exist.")

        for facility in facilities:
            metric = refresh_facility_daily_metric(facility)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Refreshed daily metrics for {facility.code} on {metric.date}",
                ),
            )
