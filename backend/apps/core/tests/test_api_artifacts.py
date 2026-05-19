import json

import pytest
from django.core.management import call_command
from django.urls import reverse

from apps.core.api_artifacts import build_postman_collection


@pytest.mark.django_db
def test_schema_endpoint_is_available(client):
    response = client.get(reverse("api-schema"), HTTP_ACCEPT="application/json")

    assert response.status_code == 200
    payload = json.loads(response.content)
    assert payload["info"]["title"] == "ShieldTB Backend API"
    assert "/api/v1/auth/login/" in payload["paths"]


def test_build_postman_collection_marks_public_endpoints_as_noauth():
    schema = {
        "paths": {
            "/api/v1/auth/login/": {
                "post": {
                    "summary": "Log in",
                    "tags": ["Auth"],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "username": {"type": "string"},
                                        "password": {"type": "string"},
                                    },
                                }
                            }
                        }
                    },
                }
            }
        },
        "components": {"schemas": {}},
    }

    collection = build_postman_collection(schema)
    request = collection["item"][0]["item"][0]
    assert request["request"]["auth"]["type"] == "noauth"


@pytest.mark.django_db
def test_export_api_artifacts_command_writes_files(tmp_path):
    output_dir = tmp_path / "generated"

    call_command("export_api_artifacts", output_dir=str(output_dir))

    openapi_path = output_dir / "openapi.json"
    collection_path = output_dir / "ShieldTB.postman_collection.json"
    environment_path = output_dir / "ShieldTB.local.postman_environment.json"

    assert openapi_path.exists()
    assert collection_path.exists()
    assert environment_path.exists()

    collection = json.loads(collection_path.read_text(encoding="utf-8"))
    environment = json.loads(environment_path.read_text(encoding="utf-8"))

    assert collection["info"]["name"] == "ShieldTB Backend"
    assert environment["name"] == "ShieldTB Local"
