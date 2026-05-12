from rest_framework.routers import DefaultRouter

from apps.accounts.views import UserViewSet
from apps.facilities.views import FacilityViewSet

router = DefaultRouter()
router.register("facilities", FacilityViewSet, basename="facility")
router.register("users", UserViewSet, basename="user")
