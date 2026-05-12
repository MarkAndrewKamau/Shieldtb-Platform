from django.utils.encoding import force_str

from apps.audit.models import AuditEvent

SENSITIVE_META_KEYS = {"authorization", "cookie", "password", "token", "refresh", "access"}


def record_audit_event(
    request,
    action: str,
    resource_type: str,
    resource_id: object = "",
    metadata: dict | None = None,
    actor=None,
) -> AuditEvent:
    actor = actor or getattr(request, "user", None)
    if not getattr(actor, "is_authenticated", False):
        actor = None

    return AuditEvent.objects.create(
        actor=actor,
        action=action,
        resource_type=resource_type,
        resource_id=force_str(resource_id) if resource_id is not None else "",
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
        metadata=redact_metadata(metadata or {}),
    )


def get_client_ip(request) -> str | None:
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def redact_metadata(metadata: dict) -> dict:
    redacted = {}
    for key, value in metadata.items():
        if key.lower() in SENSITIVE_META_KEYS:
            redacted[key] = "[redacted]"
        else:
            redacted[key] = value
    return redacted
