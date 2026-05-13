from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin")


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin")


class CanManageUsers(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.role == "admin")


def user_can_access_facility(user, facility_id: int | None) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.role == "admin":
        return True
    return bool(user.facility_id and facility_id and user.facility_id == facility_id)


def scoped_facility_queryset(user, queryset):
    if user.role == "admin":
        return queryset
    if user.facility_id:
        return queryset.filter(facility_id=user.facility_id)
    return queryset.none()
