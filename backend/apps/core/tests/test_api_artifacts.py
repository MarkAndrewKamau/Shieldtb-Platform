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
    assert "/health/" in payload["paths"]
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
    request = find_collection_request(collection, "Auth", "Log in")
    assert request["request"]["auth"]["type"] == "noauth"


def test_build_postman_collection_uses_tailored_examples_and_variables():
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
            },
            "/api/v1/households/": {
                "post": {
                    "summary": "Create household trace",
                    "tags": ["Households"],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "index_patient": {"type": "integer"},
                                    },
                                }
                            }
                        }
                    },
                }
            },
        },
        "components": {"schemas": {}},
    }

    collection = build_postman_collection(schema)
    assert any(
        variable["key"] == "householdId" for variable in collection["variable"]
    )

    login_request = find_collection_request(collection, "Auth", "Log in")
    assert "{{username}}" in login_request["request"]["body"]["raw"]

    household_request = find_collection_request(collection, "Households", "Create household trace")
    assert '"index_patient": {{patientId}}' in household_request["request"]["body"]["raw"]
    assert household_request["event"][0]["script"]["exec"][-1] == "}"


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
    assert any(value["key"] == "householdId" for value in environment["values"])


def find_collection_request(collection: dict, folder_name: str, request_name: str) -> dict:
    for folder in collection["item"]:
        if folder["name"] != folder_name:
            continue
        for request in folder["item"]:
            if request["name"] == request_name:
                return request
    raise AssertionError(f"Request {request_name!r} not found in folder {folder_name!r}.")
