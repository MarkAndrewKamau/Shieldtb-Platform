"""Django settings for the ShieldTB backend."""

from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

from apps.households.choices import HouseholdContactScreeningStatus
from apps.notifications.choices import NotificationChannel, NotificationStatus
from apps.tasks.choices import WorkflowTaskStatus

from .utils import env, env_bool, env_list

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = env_list("DJANGO_SECRET_KEY", ["unsafe-dev-secret"])[0]
DEBUG = env_bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", ["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "apps.core",
    "apps.facilities",
    "apps.accounts",
    "apps.patients",
    "apps.clinical",
    "apps.risk",
    "apps.households",
    "apps.tasks",
    "apps.notifications",
    "apps.audit",
    "apps.analytics",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default="postgres://shieldtb:shieldtb@localhost:5432/shieldtb",
        conn_max_age=600,
    )
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.accounts.authentication.CookieJWTAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", [])
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", [])

JWT_AUTH_COOKIE = "shieldtb_access"
JWT_REFRESH_COOKIE = "shieldtb_refresh"
JWT_COOKIE_SECURE = env_bool("JWT_COOKIE_SECURE", default=not DEBUG)
JWT_COOKIE_SAMESITE = env("JWT_COOKIE_SAMESITE", "Strict")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": env("JWT_ALGORITHM", "HS256"),
    "SIGNING_KEY": env("JWT_SIGNING_KEY", SECRET_KEY),
    "VERIFYING_KEY": env("JWT_VERIFYING_KEY", ""),
    "AUDIENCE": env("JWT_AUDIENCE", "shieldtb-api"),
    "ISSUER": env("JWT_ISSUER", "shieldtb-auth"),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "JTI_CLAIM": "jti",
    "LEEWAY": 0,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "ShieldTB Backend API",
    "DESCRIPTION": (
        "API for ShieldTB Kenya clinical workflows, patient registry, "
        "risk scoring, and facility-scoped operations."
    ),
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/v1",
    "COMPONENT_SPLIT_REQUEST": True,
    "TAGS": [
        {"name": "Health", "description": "Service liveness and readiness probes."},
        {"name": "Auth", "description": "Authentication and session lifecycle."},
        {"name": "Facilities", "description": "Facility registry and administration."},
        {"name": "Users", "description": "User administration."},
        {"name": "Patients", "description": "Patient registry."},
        {"name": "Households", "description": "Household tracing and contact management."},
        {"name": "Clinical", "description": "Clinical encounters and structured intake."},
        {"name": "Risk", "description": "Risk assessments derived from intake data."},
        {"name": "Tasks", "description": "Workflow tasks for CHWs and care-team staff."},
        {"name": "Notifications", "description": "Notification records and delivery state."},
    ],
    "ENUM_NAME_OVERRIDES": {
        "HouseholdContactStatusEnum": HouseholdContactScreeningStatus,
        "WorkflowTaskStatusEnum": WorkflowTaskStatus,
        "NotificationChannelEnum": NotificationChannel,
        "NotificationStatusEnum": NotificationStatus,
    },
    "SECURITY": [{"BearerAuth": []}],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
}
