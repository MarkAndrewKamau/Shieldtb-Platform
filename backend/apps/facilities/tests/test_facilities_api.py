import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.facilities.models import Facility


@pytest.fixture
def facilities(db):
    first = Facility.objects.create(
        name="Kibera Dispensary",
        code="KE-NBO-KIB-001",
        facility_type=Facility.FacilityType.DISPENSARY,
    )
    second = Facility.objects.create(
        name="Mbagathi Hospital",
        code="KE-NBO-MBA-001",
        facility_type=Facility.FacilityType.HOSPITAL,
    )
    return first, second


@pytest.mark.django_db
def test_admin_can_create_facility(facilities):
    admin = User.objects.create_user(username="admin", password="password", role=User.Role.ADMIN)
    client = APIClient()
    client.force_authenticate(admin)

    response = client.post(
        reverse("facility-list"),
        {
            "name": "Langata Health Centre",
            "code": "KE-NBO-LAN-001",
            "facility_type": Facility.FacilityType.HEALTH_CENTRE,
        },
        format="json",
    )

    assert response.status_code == 201
    assert Facility.objects.filter(code="KE-NBO-LAN-001").exists()


@pytest.mark.django_db
def test_non_admin_can_only_see_own_facility(facilities):
    own_facility, other_facility = facilities
    user = User.objects.create_user(
        username="chw",
        password="password",
        role=User.Role.CHW,
        facility=own_facility,
    )
    client = APIClient()
    client.force_authenticate(user)

    response = client.get(reverse("facility-list"))

    assert response.status_code == 200
    assert [facility["id"] for facility in response.data] == [own_facility.id]
    assert other_facility.id not in [facility["id"] for facility in response.data]


@pytest.mark.django_db
def test_non_admin_cannot_create_facility(facilities):
    user = User.objects.create_user(username="chw", password="password", role=User.Role.CHW)
    client = APIClient()
    client.force_authenticate(user)

    response = client.post(
        reverse("facility-list"),
        {
            "name": "Blocked Facility",
            "code": "KE-NBO-BLOCKED",
            "facility_type": Facility.FacilityType.DISPENSARY,
        },
        format="json",
    )

    assert response.status_code == 403
