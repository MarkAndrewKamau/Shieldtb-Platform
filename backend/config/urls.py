from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def health_check(_request):
    return JsonResponse({"status": "ok", "service": "shieldtb-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
]

