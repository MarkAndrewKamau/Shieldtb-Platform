from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.api_artifacts import export_openapi_schema, export_postman_artifacts


class Command(BaseCommand):
    help = "Export OpenAPI and Postman artifacts for the backend API."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            default="docs/generated",
            help="Directory for generated API artifacts.",
        )

    def handle(self, *args, **options):
        repo_root = settings.BASE_DIR
        output_dir = Path(options["output_dir"])
        if not output_dir.is_absolute():
            output_dir = repo_root / output_dir
        openapi_path = output_dir / "openapi.json"

        schema = export_openapi_schema(openapi_path)
        collection_path, environment_path = export_postman_artifacts(output_dir, schema)

        self.stdout.write(self.style.SUCCESS(f"Exported {openapi_path}"))
        self.stdout.write(self.style.SUCCESS(f"Exported {collection_path}"))
        self.stdout.write(self.style.SUCCESS(f"Exported {environment_path}"))
