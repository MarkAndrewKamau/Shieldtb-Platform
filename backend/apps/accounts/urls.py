from django.urls import path

from apps.accounts.views import (
    LogoutView,
    MeView,
    SecureTokenObtainPairView,
    SecureTokenRefreshView,
)

urlpatterns = [
    path("login/", SecureTokenObtainPairView.as_view(), name="token-login"),
    path("refresh/", SecureTokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="token-logout"),
    path("me/", MeView.as_view(), name="current-user"),
]
