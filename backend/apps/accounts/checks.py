from django.conf import settings
from django.core.checks import Error, Warning, register


@register()
def jwt_security_checks(app_configs, **kwargs):
    errors = []
    algorithm = settings.SIMPLE_JWT["ALGORITHM"]
    signing_key = settings.SIMPLE_JWT["SIGNING_KEY"]

    if algorithm.lower() == "none":
        errors.append(
            Error(
                "JWT algorithm cannot be 'none'.",
                id="shieldtb.E001",
            )
        )

    if algorithm.startswith("HS") and not settings.DEBUG and len(signing_key) < 32:
        errors.append(
            Error(
                "JWT_SIGNING_KEY must be at least 32 characters when using HS algorithms.",
                id="shieldtb.E002",
            )
        )
    elif algorithm.startswith("HS") and len(signing_key) < 32:
        errors.append(
            Warning(
                "JWT_SIGNING_KEY should be at least 32 characters.",
                id="shieldtb.W001",
            )
        )

    return errors
