from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from config.api import router


def health_check(_request):
    return JsonResponse({"status": "ok", "service": "shieldtb-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/", include(router.urls)),
]
