from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core.views import HealthCheckView
from config.api import router

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-schema-swagger-ui",
    ),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/", include(router.urls)),
]
