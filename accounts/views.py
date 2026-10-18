from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.exceptions import NotFound, Throttled
from rest_framework.response import Response
from rest_framework.views import APIView

from . import ratelimit, services
from .models import EmailConfirmation
from .serializers import RegisterSerializer, ResendConfirmationSerializer, UserSerializer

RESEND_PER_EMAIL = {"limit": 1, "period": 60}
RESEND_PER_IP = {"limit": 10, "period": 3600}


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=RegisterSerializer, responses={201: UserSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.register_user(**serializer.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class ResendConfirmationView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=ResendConfirmationSerializer, responses={200: None, 429: None})
    def post(self, request):
        serializer = ResendConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        ip = ratelimit.client_ip(request)
        if not ratelimit.is_allowed(f"resend:ip:{ip}", **RESEND_PER_IP):
            raise Throttled(wait=RESEND_PER_IP["period"])
        if not ratelimit.is_allowed(f"resend:email:{email}", **RESEND_PER_EMAIL):
            raise Throttled(wait=RESEND_PER_EMAIL["period"])

        services.resend_confirmation(email=email)
        return Response({"detail": "Если аккаунт существует и не подтверждён, письмо отправлено."})


class ConfirmEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses={200: UserSerializer})
    def get(self, request, token):
        try:
            user = services.confirm_email(token=token)
        except EmailConfirmation.DoesNotExist:
            raise NotFound("Ссылка недействительна или уже использована.")
        return Response(UserSerializer(user).data)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: UserSerializer})
    def get(self, request):
        return Response(UserSerializer(request.user).data)
