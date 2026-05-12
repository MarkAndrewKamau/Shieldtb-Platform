import base64
import json
from datetime import timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import AccessTokenBlocklist, User
from apps.audit.models import AuditEvent
from apps.facilities.models import Facility


@pytest.fixture
def facility(db):
    return Facility.objects.create(
        name="Kibera Dispensary",
        code="KE-NBO-KIB-001",
        facility_type=Facility.FacilityType.DISPENSARY,
        county="Nairobi",
        sub_county="Kibra",
    )


@pytest.fixture
def clinician(db, facility):
    user = User.objects.create_user(
        username="clinician",
        password="a-very-secure-test-password",
        role=User.Role.CLINICIAN,
        facility=facility,
    )
    return user


@pytest.mark.django_db
def test_login_sets_httponly_cookies_without_returning_raw_tokens(clinician):
    client = APIClient()

    response = client.post(
        reverse("token-login"),
        {"username": "clinician", "password": "a-very-secure-test-password"},
        format="json",
    )

    assert response.status_code == 200
    assert "access" not in response.data
    assert "refresh" not in response.data
    assert response.data["user"]["role"] == User.Role.CLINICIAN

    access_cookie = response.cookies[settings.JWT_AUTH_COOKIE]
    refresh_cookie = response.cookies[settings.JWT_REFRESH_COOKIE]
    assert access_cookie["httponly"]
    assert refresh_cookie["httponly"]
    assert access_cookie["samesite"] == "Strict"
    assert refresh_cookie["samesite"] == "Strict"
    assert AuditEvent.objects.filter(action="auth.login", actor=clinician).exists()


@pytest.mark.django_db
def test_logout_blocks_current_access_token(clinician):
    client = APIClient()
    login_response = client.post(
        reverse("token-login"),
        {"username": "clinician", "password": "a-very-secure-test-password"},
        format="json",
    )
    access = login_response.cookies[settings.JWT_AUTH_COOKIE].value
    refresh = login_response.cookies[settings.JWT_REFRESH_COOKIE].value

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    logout_response = client.post(reverse("token-logout"), {"refresh": refresh}, format="json")

    assert logout_response.status_code == 200
    assert AccessTokenBlocklist.objects.count() == 1

    me_response = client.get(reverse("current-user"))
    assert me_response.status_code == 401


@pytest.mark.django_db
def test_none_algorithm_token_is_rejected(clinician):
    client = APIClient()
    login_response = client.post(
        reverse("token-login"),
        {"username": "clinician", "password": "a-very-secure-test-password"},
        format="json",
    )
    token = login_response.cookies[settings.JWT_AUTH_COOKIE].value
    _header, payload, _signature = token.split(".")
    none_header = _base64url({"alg": "none", "typ": "JWT"})
    forged = f"{none_header}.{payload}."

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {forged}")
    response = client.get(reverse("current-user"))

    assert response.status_code == 401


def test_jwt_security_settings_are_strict():
    assert settings.SIMPLE_JWT["ALGORITHM"] != "none"
    assert settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] == timedelta(minutes=15)
    assert settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"] is True
    assert settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"] is True
    assert settings.SIMPLE_JWT["ISSUER"] == "shieldtb-auth"
    assert settings.SIMPLE_JWT["AUDIENCE"] == "shieldtb-api"


def _base64url(payload: dict) -> str:
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    return encoded.rstrip("=")
