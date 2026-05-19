import json
import re
from collections import defaultdict
from pathlib import Path

from drf_spectacular.generators import SchemaGenerator

TAG_ORDER = ["Auth", "Facilities", "Users", "Patients", "Households", "Clinical", "Risk", "Tasks"]


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
                build_postman_request(path, method.upper(), operation, schema),
            )

    ordered_tags = [tag for tag in TAG_ORDER if tag in grouped_items]
    ordered_tags.extend(sorted(tag for tag in grouped_items if tag not in TAG_ORDER))

    return {
        "info": {
            "name": "ShieldTB Backend",
            "description": (
                "Generated from the ShieldTB OpenAPI schema. "
                "Use the Postman Desktop Agent for localhost requests."
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
        "variable": [
            {"key": "baseUrl", "value": "http://localhost:8000"},
            {"key": "accessToken", "value": ""},
            {"key": "refreshToken", "value": ""},
            {"key": "facilityId", "value": ""},
            {"key": "patientId", "value": ""},
            {"key": "encounterId", "value": ""},
            {"key": "userId", "value": ""},
        ],
        "item": [{"name": tag, "item": grouped_items[tag]} for tag in ordered_tags],
    }


def build_postman_environment() -> dict:
    return {
        "name": "ShieldTB Local",
        "values": [
            {
                "key": "baseUrl",
                "value": "http://localhost:8000",
                "type": "default",
                "enabled": True,
            },
            {"key": "username", "value": "", "type": "default", "enabled": True},
            {"key": "password", "value": "", "type": "secret", "enabled": True},
            {"key": "email", "value": "", "type": "default", "enabled": True},
            {"key": "accessToken", "value": "", "type": "secret", "enabled": True},
            {"key": "refreshToken", "value": "", "type": "secret", "enabled": True},
            {"key": "facilityId", "value": "", "type": "default", "enabled": True},
            {"key": "patientId", "value": "", "type": "default", "enabled": True},
            {"key": "encounterId", "value": "", "type": "default", "enabled": True},
            {"key": "userId", "value": "", "type": "default", "enabled": True},
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
        request["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(example_from_schema(body_schema, schema), indent=2),
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


def variable_capture_script(variable_name: str) -> str:
    return f"""const response = pm.response.json();
if (response && response.id) {{
  pm.environment.set("{variable_name}", response.id);
}}"""


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
