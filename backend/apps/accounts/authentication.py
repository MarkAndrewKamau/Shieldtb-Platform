from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.models import AccessTokenBlocklist


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate JWTs from Authorization headers or HttpOnly cookies.

    Header tokens are useful for API clients. Browser clients should use the
    HttpOnly access cookie; unsafe cookie-authenticated requests must pass CSRF.
    """

    def authenticate(self, request):
        raw_token = self._get_raw_token(request)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        self._reject_blocked_token(validated_token)

        if self._using_cookie(request):
            self._enforce_csrf(request)

        return self.get_user(validated_token), validated_token

    def _get_raw_token(self, request):
        header = self.get_header(request)
        if header is not None:
            return self.get_raw_token(header)
        return request.COOKIES.get(settings.JWT_AUTH_COOKIE)

    def _using_cookie(self, request) -> bool:
        return self.get_header(request) is None and settings.JWT_AUTH_COOKIE in request.COOKIES

    def _reject_blocked_token(self, validated_token) -> None:
        jti = validated_token.get(settings.SIMPLE_JWT["JTI_CLAIM"])
        if jti and AccessTokenBlocklist.is_blocked(jti):
            raise exceptions.AuthenticationFailed("Token has been revoked.", code="token_revoked")

    def _enforce_csrf(self, request) -> None:
        reason = CsrfViewMiddleware(lambda req: None).process_view(request, None, (), {})
        if reason:
            raise exceptions.PermissionDenied(f"CSRF failed: {reason}")
