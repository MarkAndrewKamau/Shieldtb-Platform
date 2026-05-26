from datetime import UTC, datetime

from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import AccessTokenBlocklist, User
from apps.accounts.permissions import CanManageUsers
from apps.accounts.serializers import (
    DetailSerializer,
    LoginRequestSerializer,
    RefreshResponseSerializer,
    RefreshRequestSerializer,
    ShieldTBTokenObtainPairSerializer,
    SignupSerializer,
    UserEnvelopeSerializer,
    UserSerializer,
)
from apps.audit.services import record_audit_event


@extend_schema(
    tags=["Auth"],
    request=LoginRequestSerializer,
    responses={200: UserEnvelopeSerializer},
    summary="Log in",
    description=(
        "Authenticates a user. Browser clients default to HttpOnly JWT cookies; "
        'native clients may request `auth_mode: "token"` to receive tokens in the body.'
    ),
)
class SecureTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = ShieldTBTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_data = serializer.validated_data
        refresh = token_data.pop("refresh")
        access = token_data.pop("access")
        auth_mode = request.data.get("auth_mode", "cookie")

        response_payload = dict(token_data)
        if auth_mode == "token":
            response_payload["access"] = access
            response_payload["refresh"] = refresh
        response = Response(response_payload, status=status.HTTP_200_OK)
        if auth_mode != "token":
            set_auth_cookies(response, access=access, refresh=refresh)
        record_audit_event(
            request,
            action="auth.login",
            resource_type="User",
            resource_id=serializer.user.id,
            actor=serializer.user,
        )
        return response


@extend_schema(
    tags=["Auth"],
    request=RefreshRequestSerializer,
    responses={200: RefreshResponseSerializer},
    summary="Refresh token",
    description=(
        "Rotates the refresh token. Browser clients default to updated HttpOnly cookies; "
        'native clients may request `auth_mode: "token"` to receive fresh tokens in the body.'
    ),
)
class SecureTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.copy()
        auth_mode = data.get("auth_mode", "cookie")
        data["refresh"] = data.get("refresh") or request.COOKIES.get(settings.JWT_REFRESH_COOKIE)
        serializer = TokenRefreshSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        token_data = serializer.validated_data
        response_payload = {"detail": "Token refreshed."}
        if auth_mode == "token":
            response_payload["access"] = token_data["access"]
            if token_data.get("refresh"):
                response_payload["refresh"] = token_data["refresh"]
        response = Response(response_payload, status=status.HTTP_200_OK)
        if auth_mode != "token":
            set_auth_cookies(
                response,
                access=token_data["access"],
                refresh=token_data.get("refresh"),
            )
        return response


@extend_schema(
    tags=["Auth"],
    request=SignupSerializer,
    responses={201: UserEnvelopeSerializer},
    summary="Sign up",
    description=(
        "Creates a non-admin user account. Browser clients default to HttpOnly JWT cookies; "
        'native clients may request `auth_mode: "token"` to receive tokens in the body.'
    ),
)
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        auth_mode = request.data.get("auth_mode", "cookie")

        refresh = ShieldTBTokenObtainPairSerializer.get_token(user)
        access = refresh.access_token

        response_payload = {"user": UserSerializer(user).data}
        if auth_mode == "token":
            response_payload["access"] = str(access)
            response_payload["refresh"] = str(refresh)
        response = Response(response_payload, status=status.HTTP_201_CREATED)
        if auth_mode != "token":
            set_auth_cookies(response, access=str(access), refresh=str(refresh))
        record_audit_event(
            request,
            action="auth.signup",
            resource_type="User",
            resource_id=user.id,
            actor=user,
        )
        return response


@extend_schema(
    tags=["Auth"],
    request=RefreshRequestSerializer,
    responses={200: DetailSerializer},
    summary="Log out",
    description="Revokes the current access token and blacklists the refresh token when provided.",
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE) or request.data.get("refresh")
        if refresh:
            try:
                RefreshToken(refresh).blacklist()
            except TokenError:
                pass

        block_current_access_token(request)
        record_audit_event(
            request,
            action="auth.logout",
            resource_type="User",
            resource_id=request.user.id,
        )

        response = Response({"detail": "Logged out."}, status=status.HTTP_200_OK)
        clear_auth_cookies(response)
        return response


@extend_schema(
    tags=["Auth"],
    responses={200: UserSerializer},
    summary="Current user",
    description="Returns the authenticated user profile.",
)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


@extend_schema_view(
    list=extend_schema(tags=["Users"], summary="List users"),
    retrieve=extend_schema(tags=["Users"], summary="Retrieve user"),
    create=extend_schema(tags=["Users"], summary="Create user"),
    update=extend_schema(tags=["Users"], summary="Update user"),
    partial_update=extend_schema(tags=["Users"], summary="Partially update user"),
    destroy=extend_schema(tags=["Users"], summary="Delete user"),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("facility").all()
    serializer_class = UserSerializer
    permission_classes = [CanManageUsers]
    filterset_fields = ["role", "facility", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name", "phone"]

    def perform_create(self, serializer):
        user = serializer.save()
        record_audit_event(self.request, "users.create", "User", user.id)

    def perform_update(self, serializer):
        user = serializer.save()
        record_audit_event(self.request, "users.update", "User", user.id)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        record_audit_event(request, "users.deactivate", "User", user.id)
        return Response(UserSerializer(user).data)


def set_auth_cookies(response: Response, *, access: str, refresh: str | None = None) -> None:
    response.set_cookie(
        settings.JWT_AUTH_COOKIE,
        access,
        max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path="/",
    )
    if refresh:
        response.set_cookie(
            settings.JWT_REFRESH_COOKIE,
            refresh,
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            path="/api/v1/auth/",
        )


def clear_auth_cookies(response: Response) -> None:
    for cookie_name in [settings.JWT_AUTH_COOKIE, settings.JWT_REFRESH_COOKIE]:
        response.delete_cookie(cookie_name, path="/")
        response.delete_cookie(cookie_name, path="/api/v1/auth/")


def block_current_access_token(request) -> None:
    token = getattr(request, "auth", None)
    if not token:
        return

    jti = token.get(settings.SIMPLE_JWT["JTI_CLAIM"])
    exp = token.get("exp")
    if not jti or not exp:
        return

    expires_at = datetime.fromtimestamp(exp, tz=UTC)
    AccessTokenBlocklist.objects.get_or_create(
        jti=jti,
        defaults={
            "expires_at": expires_at,
            "revoked_by": request.user,
            "reason": "logout",
        },
    )
