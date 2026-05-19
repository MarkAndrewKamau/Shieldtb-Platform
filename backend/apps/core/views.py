from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


@extend_schema(
    tags=["Health"],
    auth=[],
    responses={
        200: inline_serializer(
            name="HealthCheckResponse",
            fields={
                "status": serializers.CharField(),
                "service": serializers.CharField(),
            },
        ),
    },
    summary="Health check",
    description="Simple liveness endpoint for local development and deployment probes.",
)
class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, _request):
        return Response({"status": "ok", "service": "shieldtb-api"})
