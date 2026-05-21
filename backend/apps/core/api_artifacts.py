import json
import re
from collections import defaultdict
from pathlib import Path

from drf_spectacular.generators import SchemaGenerator

TAG_ORDER = [
    "Health",
    "Auth",
    "Facilities",
    "Users",
    "Patients",
    "Households",
    "Clinical",
    "Risk",
    "Tasks",
    "Analytics",
    "Notifications",
]

RAW_MARKER_PREFIX = "__POSTMAN_RAW__"
RAW_MARKER_SUFFIX = "__"


def raw_variable(name: str) -> str:
    return f"{RAW_MARKER_PREFIX}{{{{{name}}}}}{RAW_MARKER_SUFFIX}"

POSTMAN_VARIABLES = [
    ("baseUrl", "http://localhost:8000", "default"),
    ("username", "", "default"),
    ("password", "", "secret"),
    ("email", "", "default"),
    ("accessToken", "", "secret"),
    ("refreshToken", "", "secret"),
    ("facilityId", "", "default"),
    ("patientId", "", "default"),
    ("encounterId", "", "default"),
    ("userId", "", "default"),
    ("householdId", "", "default"),
    ("contactId", "", "default"),
]

REQUEST_BODY_OVERRIDES = {
    ("POST", "/api/v1/auth/login/"): {
        "username": "{{username}}",
        "password": "{{password}}",
    },
    ("POST", "/api/v1/auth/refresh/"): {
        "refresh": "{{refreshToken}}",
    },
    ("POST", "/api/v1/auth/logout/"): {
        "refresh": "{{refreshToken}}",
    },
    ("POST", "/api/v1/auth/signup/"): {
        "username": "{{username}}",
        "email": "{{email}}",
        "first_name": "New",
        "last_name": "User",
        "role": "chw",
        "facility": raw_variable("facilityId"),
        "phone": "+254700000123",
        "password": "{{password}}",
    },
    ("POST", "/api/v1/facilities/"): {
        "name": "Kibera Dispensary",
        "code": "KE-NBO-KIB-001",
        "facility_type": "dispensary",
        "county": "Nairobi",
        "sub_county": "Kibra",
        "ward": "Laini Saba",
        "phone": "+254700000100",
        "is_active": True,
    },
    ("PUT", "/api/v1/facilities/{id}/"): {
        "name": "Kibera Dispensary",
        "code": "KE-NBO-KIB-001",
        "facility_type": "dispensary",
        "county": "Nairobi",
        "sub_county": "Kibra",
        "ward": "Laini Saba",
        "phone": "+254700000100",
        "is_active": True,
    },
    ("PATCH", "/api/v1/facilities/{id}/"): {
        "phone": "+254700000101",
    },
    ("POST", "/api/v1/users/"): {
        "username": "clinician1",
        "email": "clinician1@example.com",
        "first_name": "Amina",
        "last_name": "Otieno",
        "role": "clinician",
        "facility": raw_variable("facilityId"),
        "phone": "+254700000200",
        "is_active": True,
        "must_reset_password": False,
        "password": "VerySecurePassword123!",
    },
    ("PUT", "/api/v1/users/{id}/"): {
        "username": "clinician1",
        "email": "clinician1@example.com",
        "first_name": "Amina",
        "last_name": "Otieno",
        "role": "clinician",
        "facility": raw_variable("facilityId"),
        "phone": "+254700000200",
        "is_active": True,
        "must_reset_password": False,
    },
    ("PATCH", "/api/v1/users/{id}/"): {
        "phone": "+254700000201",
        "must_reset_password": True,
    },
    ("POST", "/api/v1/users/{id}/deactivate/"): {},
    ("POST", "/api/v1/patients/"): {
        "external_id": "P-001",
        "given_name": "Amina",
        "family_name": "Otieno",
        "date_of_birth": "1993-08-21",
        "sex": "female",
        "phone": "+254700000001",
        "national_id_hash": "hashed-national-id",
        "facility": raw_variable("facilityId"),
        "enrollment_source": "art_clinic",
        "consented_at": "2026-05-19T09:00:00Z",
        "is_active": True,
    },
    ("PUT", "/api/v1/patients/{id}/"): {
        "external_id": "P-001",
        "given_name": "Amina",
        "family_name": "Otieno",
        "date_of_birth": "1993-08-21",
        "sex": "female",
        "phone": "+254700000001",
        "national_id_hash": "hashed-national-id",
        "facility": raw_variable("facilityId"),
        "enrollment_source": "art_clinic",
        "consented_at": "2026-05-19T09:00:00Z",
        "is_active": True,
    },
    ("PATCH", "/api/v1/patients/{id}/"): {
        "phone": "+254700000002",
    },
    ("POST", "/api/v1/clinical/intakes/"): {
        "patient": raw_variable("patientId"),
        "occurred_at": "2026-05-19T09:30:00Z",
        "notes": "Initial ART clinic TB risk intake.",
        "cough": True,
        "fever": False,
        "night_sweats": False,
        "weight_loss": True,
        "hiv_positive": True,
        "pregnant": False,
        "postpartum": False,
        "diabetes": False,
        "sle_or_autoimmune": False,
        "ckd": False,
        "on_immunosuppressants": False,
        "previous_tb": False,
        "household_tb_contact": True,
        "crowded_housing": True,
        "poor_ventilation": True,
        "medication_history": {
            "current": ["tenofovir", "lamivudine", "dolutegravir"],
        },
    },
    ("POST", "/api/v1/households/"): {
        "index_patient": raw_variable("patientId"),
        "assigned_chw": raw_variable("userId"),
        "county": "Nairobi",
        "sub_county": "Kibra",
        "ward": "Laini Saba",
        "village": "Village A",
        "address_description": "Near the community hall.",
        "latitude": -1.3132,
        "longitude": 36.7891,
        "contact_entries": [
            {
                "full_name": "Mary Otieno",
                "age_years": 34,
                "phone": "+254700000301",
                "relationship_to_index": "Spouse",
                "immunocompromised": False,
                "status": "pending",
            },
            {
                "full_name": "Kevin Otieno",
                "age_years": 6,
                "relationship_to_index": "Child",
                "immunocompromised": True,
                "status": "pending",
            },
        ],
    },
    ("PUT", "/api/v1/households/{id}/"): {
        "index_patient": raw_variable("patientId"),
        "assigned_chw": raw_variable("userId"),
        "county": "Nairobi",
        "sub_county": "Kibra",
        "ward": "Laini Saba",
        "village": "Village A",
        "address_description": "Near the community hall.",
        "latitude": -1.3132,
        "longitude": 36.7891,
    },
    ("PATCH", "/api/v1/households/{id}/"): {
        "assigned_chw": raw_variable("userId"),
        "address_description": "Updated landmark for follow-up.",
    },
    ("POST", "/api/v1/household-contacts/"): {
        "household": raw_variable("householdId"),
        "patient": raw_variable("patientId"),
        "full_name": "Grace Achieng",
        "age_years": 28,
        "phone": "+254700000302",
        "relationship_to_index": "Sibling",
        "immunocompromised": False,
        "status": "pending",
    },
    ("PUT", "/api/v1/household-contacts/{id}/"): {
        "household": raw_variable("householdId"),
        "patient": raw_variable("patientId"),
        "full_name": "Grace Achieng",
        "age_years": 28,
        "phone": "+254700000302",
        "relationship_to_index": "Sibling",
        "immunocompromised": False,
        "status": "screened",
    },
    ("PATCH", "/api/v1/household-contacts/{id}/"): {
        "status": "screened",
    },
    ("POST", "/api/v1/workflow-tasks/{id}/assign/"): {
        "assigned_to": raw_variable("userId"),
    },
    ("POST", "/api/v1/workflow-tasks/{id}/update_status/"): {
        "status": "in_progress",
    },
    ("POST", "/api/v1/analytics/daily-metrics/refresh/"): {
        "facility": raw_variable("facilityId"),
    },
}

REQUEST_ORDER = {
    ("GET", "/health/"): 10,
    ("POST", "/api/v1/auth/signup/"): 20,
    ("POST", "/api/v1/auth/login/"): 30,
    ("GET", "/api/v1/auth/me/"): 40,
    ("POST", "/api/v1/auth/refresh/"): 50,
    ("POST", "/api/v1/auth/logout/"): 60,
    ("GET", "/api/v1/facilities/"): 100,
    ("POST", "/api/v1/facilities/"): 110,
    ("GET", "/api/v1/users/"): 200,
    ("POST", "/api/v1/users/"): 210,
    ("GET", "/api/v1/patients/"): 300,
    ("POST", "/api/v1/patients/"): 310,
    ("GET", "/api/v1/households/"): 400,
    ("POST", "/api/v1/households/"): 410,
    ("GET", "/api/v1/household-contacts/"): 420,
    ("POST", "/api/v1/household-contacts/"): 430,
    ("GET", "/api/v1/clinical/encounters/"): 500,
    ("POST", "/api/v1/clinical/intakes/"): 510,
    ("GET", "/api/v1/risk-assessments/"): 600,
    ("GET", "/api/v1/workflow-tasks/"): 700,
    ("POST", "/api/v1/workflow-tasks/{id}/assign/"): 710,
    ("POST", "/api/v1/workflow-tasks/{id}/update_status/"): 720,
    ("GET", "/api/v1/analytics/facility-summaries/"): 800,
    ("GET", "/api/v1/analytics/daily-metrics/"): 810,
    ("POST", "/api/v1/analytics/daily-metrics/refresh/"): 820,
}


def build_openapi_schema():
    generator = SchemaGenerator()
    return generator.get_schema(request=None, public=True)


def export_openapi_schema(output_path: Path) -> dict:
    schema = build_openapi_schema()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    return schema


def export_postman_artifacts(output_dir: Path, schema: dict) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    collection_path = output_dir / "ShieldTB.postman_collection.json"
    environment_path = output_dir / "ShieldTB.local.postman_environment.json"

    collection_path.write_text(
        json.dumps(build_postman_collection(schema), indent=2) + "\n",
        encoding="utf-8",
    )
    environment_path.write_text(
        json.dumps(build_postman_environment(), indent=2) + "\n",
        encoding="utf-8",
    )
    return collection_path, environment_path


def build_postman_collection(schema: dict) -> dict:
    grouped_items = defaultdict(list)
    for path, path_item in schema.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            tag = (operation.get("tags") or ["Misc"])[0]
            grouped_items[tag].append(
                (
                    sort_key_for_request(path, method.upper()),
                    build_postman_request(path, method.upper(), operation, schema),
                ),
            )

    ordered_tags = [tag for tag in TAG_ORDER if tag in grouped_items]
    ordered_tags.extend(sorted(tag for tag in grouped_items if tag not in TAG_ORDER))

    return {
        "info": {
            "name": "ShieldTB Backend",
            "description": (
                "Generated from the ShieldTB OpenAPI schema. "
                "Use the Postman Desktop Agent for localhost requests. "
                "Run Health check first, then Sign up or Log in to populate token variables."
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{accessToken}}",
                    "type": "string",
                }
            ],
        },
        "variable": [{"key": key, "value": value} for key, value, _kind in POSTMAN_VARIABLES],
        "item": [
            {
                "name": tag,
                "item": [
                    request
                    for _key, request in sorted(
                        grouped_items[tag],
                        key=lambda item: item[0],
                    )
                ],
            }
            for tag in ordered_tags
        ],
    }


def build_postman_environment() -> dict:
    return {
        "name": "ShieldTB Local",
        "values": [
            {
                "key": key,
                "value": value,
                "type": kind,
                "enabled": True,
            }
            for key, value, kind in POSTMAN_VARIABLES
        ],
        "_postman_variable_scope": "environment",
        "_postman_exported_at": "2026-05-19T00:00:00.000Z",
        "_postman_exported_using": "Codex",
    }


def build_postman_request(path: str, method: str, operation: dict, schema: dict) -> dict:
    request = {
        "name": operation.get("summary") or operation.get("operationId") or f"{method} {path}",
        "request": {
            "method": method,
            "header": build_headers(operation),
            "url": build_url(path),
            "description": operation.get("description", ""),
        },
        "response": [],
    }

    if is_public_endpoint(path):
        request["request"]["auth"] = {"type": "noauth"}

    if "requestBody" in operation:
        body_schema = first_json_schema(operation["requestBody"], schema)
        body_example = request_body_example(path, method, body_schema, schema)
        request["request"]["body"] = {
            "mode": "raw",
            "raw": render_postman_json(body_example),
            "options": {"raw": {"language": "json"}},
        }

    events = build_events(path)
    if events:
        request["event"] = events

    return request


def build_headers(operation: dict) -> list[dict]:
    headers = [{"key": "Accept", "value": "application/json"}]
    if "requestBody" in operation:
        headers.append({"key": "Content-Type", "value": "application/json"})
    return headers


def build_url(path: str) -> dict:
    raw_path = re.sub(r"{([^}]+)}", r"{{\1}}", path)
    path_parts = [part for part in raw_path.strip("/").split("/") if part]
    return {
        "raw": "{{baseUrl}}" + raw_path,
        "host": ["{{baseUrl}}"],
        "path": path_parts,
    }


def is_public_endpoint(path: str) -> bool:
    return path in {
        "/health/",
        "/api/schema/",
        "/api/schema/swagger/",
        "/api/v1/auth/login/",
        "/api/v1/auth/signup/",
        "/api/v1/auth/refresh/",
    }


def build_events(path: str) -> list[dict]:
    if path in {
        "/api/v1/auth/login/",
        "/api/v1/auth/signup/",
        "/api/v1/auth/refresh/",
    }:
        return [postman_test_event(cookie_capture_script())]
    if path == "/api/v1/facilities/":
        return [postman_test_event(variable_capture_script("facilityId"))]
    if path == "/api/v1/patients/":
        return [postman_test_event(variable_capture_script("patientId"))]
    if path == "/api/v1/clinical/intakes/":
        return [postman_test_event(variable_capture_script("encounterId"))]
    if path == "/api/v1/users/":
        return [postman_test_event(variable_capture_script("userId"))]
    if path == "/api/v1/households/":
        return [postman_test_event(variable_capture_script("householdId"))]
    if path == "/api/v1/household-contacts/":
        return [postman_test_event(variable_capture_script("contactId"))]
    if path == "/api/v1/auth/logout/":
        return [postman_test_event(clear_auth_script())]
    return []


def postman_test_event(script: str) -> dict:
    return {
        "listen": "test",
        "script": {
            "type": "text/javascript",
            "exec": script.splitlines(),
        },
    }


def cookie_capture_script() -> str:
    return """const setCookies = pm.response.headers
  .all()
  .filter(h => h.key.toLowerCase() === "set-cookie")
  .map(h => h.value);

for (const cookie of setCookies) {
  if (cookie.startsWith("shieldtb_access=")) {
    pm.environment.set("accessToken", cookie.split(";")[0].split("=")[1]);
  }

  if (cookie.startsWith("shieldtb_refresh=")) {
    pm.environment.set("refreshToken", cookie.split(";")[0].split("=")[1]);
  }
}"""


def clear_auth_script() -> str:
    return """pm.environment.unset("accessToken");
pm.environment.unset("refreshToken");"""


def variable_capture_script(variable_name: str) -> str:
    return f"""const response = pm.response.json();
if (response && response.id) {{
  pm.environment.set("{variable_name}", response.id);
}}"""


def request_body_example(path: str, method: str, body_schema: dict, schema: dict):
    override = REQUEST_BODY_OVERRIDES.get((method, path))
    if override is not None:
        return override
    return example_from_schema(body_schema, schema)


def render_postman_json(payload: dict) -> str:
    rendered = json.dumps(payload, indent=2)
    pattern = rf'"{RAW_MARKER_PREFIX}(.*?)' + RAW_MARKER_SUFFIX + r'"'
    return re.sub(pattern, r"\1", rendered)


def sort_key_for_request(path: str, method: str) -> tuple[int, str, str]:
    return (REQUEST_ORDER.get((method, path), 9999), path, method)


def first_json_schema(request_body: dict, schema: dict) -> dict:
    content = request_body.get("content", {})
    json_content = content.get("application/json", {})
    return resolve_schema(json_content.get("schema", {}), schema)


def resolve_schema(fragment: dict, schema: dict) -> dict:
    if "$ref" in fragment:
        ref_name = fragment["$ref"].split("/")[-1]
        target = schema.get("components", {}).get("schemas", {}).get(ref_name, {})
        return resolve_schema(target, schema)
    if "allOf" in fragment:
        merged = {}
        for item in fragment["allOf"]:
            merged.update(resolve_schema(item, schema))
        return merged
    if "oneOf" in fragment:
        return resolve_schema(fragment["oneOf"][0], schema)
    if "anyOf" in fragment:
        return resolve_schema(fragment["anyOf"][0], schema)
    return fragment


def example_from_schema(fragment: dict, schema: dict):
    fragment = resolve_schema(fragment, schema)
    if "example" in fragment:
        return fragment["example"]

    if fragment.get("enum"):
        return fragment["enum"][0]

    schema_type = fragment.get("type")
    if schema_type == "object":
        properties = fragment.get("properties", {})
        required = set(fragment.get("required", []))
        example = {}
        for name, property_schema in properties.items():
            if required or name in properties:
                example[name] = example_from_schema(property_schema, schema)
        return example
    if schema_type == "array":
        item_schema = fragment.get("items", {})
        return [example_from_schema(item_schema, schema)]
    if schema_type == "boolean":
        return False
    if schema_type == "integer":
        return 1
    if schema_type == "number":
        return 1
    if schema_type == "string":
        return string_example(fragment)
    return ""


def string_example(fragment: dict) -> str:
    fmt = fragment.get("format")
    if fmt == "date-time":
        return "2026-05-19T09:00:00Z"
    if fmt == "date":
        return "2026-05-19"
    if fmt == "email":
        return "user@example.com"
    if fmt == "uuid":
        return "00000000-0000-0000-0000-000000000000"

    title = (fragment.get("title") or "").lower()
    if "username" in title:
        return "sampleuser"
    if "password" in title:
        return "a-very-secure-password"
    if "phone" in title:
        return "+254700000000"
    return "string"
