from knox.views import LoginView as KnoxLoginView
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from authentication.misc.custom_auth import CustomBasicAuthentication, CookieTokenAuthentication
from authentication.permissions import IsProfileOwnerOrReadOnly
from authentication.selectors import get_profile_with_user, get_user_with_profile_by_phone
from authentication.serializers import (
    ProfileSerializer,
    SignUpRequestSerializer,
    VerificationRequestSerializer,
    PhoneSerializer,
    PasswordResetSerializer,
    ProfileOwnerSerializer,
)
from authentication.services.profile import ProfileManagerService, PasswordManagerService
from authentication.services.verification import BaseVerificationService
from authentication.tasks import send_sms_task
from authentication.utils import make_phone_uniform
from DjangoServer.settings import MESSAGE_TEMPLATE


class LoginView(KnoxLoginView):
    authentication_classes = [CustomBasicAuthentication]


class ProfileVerificationView(APIView):
    """View, использующийся для верификации профиля пользователя по OTP коду"""

    def post(self, request, *args, **kwargs):
        serializer = VerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = make_phone_uniform(serializer.validated_data.get("phone"))
        otp = serializer.validated_data.get("otp_code")
        user = get_user_with_profile_by_phone(phone)
        profile = user.profile

        BaseVerificationService(user).verify_otp(otp)
        ProfileManagerService(profile).verify()

        return Response("verified successfully", status=status.HTTP_200_OK)


class SendVerificationCodeView(APIView):
    """View, использующийся для отправки OTP кода пользователю"""

    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = make_phone_uniform(serializer.validated_data.get("phone"))
        user = get_user_with_profile_by_phone(phone)
        otp = BaseVerificationService(user).create_otp()
        send_sms_task.delay(phone, MESSAGE_TEMPLATE.format(otp))

        return Response("verification code sent", status=status.HTTP_200_OK)


class ResetPasswordValidateTokenView(APIView):
    """View, использующийся для валидации OTP кода, без каких либо побочных эффектов"""

    def post(self, request: Request):
        serializer = VerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = make_phone_uniform(serializer.validated_data.get("phone"))
        user = get_user_with_profile_by_phone(phone)
        otp = serializer.validated_data.get("otp_code")

        BaseVerificationService(user).verify_otp(otp)

        return Response({"detail": "token is valid"}, status=status.HTTP_200_OK)


class ResetPasswordConfirmView(APIView):
    """View, использующийся для смены пароля"""

    def post(self, request: Request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = make_phone_uniform(serializer.validated_data.get("phone"))
        password = serializer.validated_data.get("password")
        otp = serializer.validated_data.get("otp_code")
        user = get_user_with_profile_by_phone(phone)

        BaseVerificationService(user).verify_otp(otp)
        PasswordManagerService(user).reset_password(new_password=password)

        return Response({"detail": "password changed"}, status=status.HTTP_200_OK)


class SignUpView(APIView):
    def post(self, request: Request):
        serializer = SignUpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_token_val, auth_token_exp, profile = ProfileManagerService.create(**serializer.validated_data)
        serialized_profile = ProfileOwnerSerializer(profile).data

        return Response(
            {"profile": serialized_profile, "token": {"token": auth_token_val, "expiry": auth_token_exp}},
            status=status.HTTP_201_CREATED,
        )


class ProfileViewSet(ViewSet):
    permission_classes = [IsProfileOwnerOrReadOnly, IsAuthenticated]
    authentication_classes = [CookieTokenAuthentication]

    def get_permissions(self):
        if self.action in ("update", "destroy", "get_my_profile"):
            return super().get_permissions()
        return [AllowAny()]

    @action(detail=False, methods=['get'], url_path='my_profile')
    def get_my_profile(self, request: Request):
        profile = request.user.profile  # type: ignore
        serialized_profile = ProfileOwnerSerializer(profile).data

        return Response(serialized_profile, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, pk: int):
        profile = get_profile_with_user(pk)
        serialized_profile = ProfileSerializer(profile).data

        return Response(serialized_profile, status=status.HTTP_200_OK)

    def update(self, request: Request, pk: int):
        profile = get_profile_with_user(pk)
        self.check_object_permissions(request, profile)

        serializer = ProfileOwnerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ProfileManagerService(profile).update(**serializer.validated_data)

        serialized_profile = ProfileOwnerSerializer(profile).data

        return Response(serialized_profile, status=status.HTTP_200_OK)

    def destroy(self, request: Request, pk: int):
        profile = get_profile_with_user(pk)
        self.check_object_permissions(request, profile)

        ProfileManagerService(profile).soft_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
