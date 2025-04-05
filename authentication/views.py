from knox.views import LoginView as KnoxLoginView
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from authentication.misc.custom_auth import CustomBasicAuthentication
from authentication.permissions import IsProfileOwnerOrReadOnly
from authentication.selectors import get_profile_with_user, get_user_with_profile_by_phone, get_otp_with_user_by_code
from authentication.serializers import ProfileSerializer, SignUpRequestSerializer, VerificationRequestSerializer, \
    PhoneSerializer, PasswordResetSerializer
from authentication.services.profile import ProfileManagerService, PasswordManagerService
from authentication.services.verification import BaseVerificationService
from authentication.tasks import send_sms_task
from authentication.utils import make_phone_uniform

MESSAGE_TEMPLATE = "Зубастый ректум приглашает вас, код {0}"


class LoginView(KnoxLoginView):
    authentication_classes = [CustomBasicAuthentication]


class ProfileVerificationView(APIView):
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
    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = make_phone_uniform(serializer.validated_data.get("phone"))
        user = get_user_with_profile_by_phone(phone)
        otp = BaseVerificationService(user).create_otp()
        send_sms_task.delay(phone, MESSAGE_TEMPLATE.format(otp))

        return Response("verification code sent", status=status.HTTP_200_OK)


class ResetPasswordValidateTokenView(APIView):
    def post(self, request: Request):
        serializer = VerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = make_phone_uniform(serializer.validated_data.get("phone"))
        user = get_user_with_profile_by_phone(phone)
        otp = serializer.validated_data.get("otp_code")

        BaseVerificationService(user).verify_otp(otp)

        return Response({"detail": "token is valid"}, status=status.HTTP_200_OK)


class ResetPasswordConfirmView(APIView):
    def post(self, request: Request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = serializer.validated_data.get("password")
        otp_code = serializer.validated_data.get("otp_code")

        otp = get_otp_with_user_by_code(otp_code)
        user = otp.user

        BaseVerificationService(user).verify_otp(otp_code)
        PasswordManagerService(user).reset_password(new_password=password)

        return Response({"detail": "password changed"}, status=status.HTTP_200_OK)


class SignUpView(APIView):
    def post(self, request: Request):
        serializer = SignUpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_token, profile = ProfileManagerService.create(**serializer.validated_data)
        serialized_profile = ProfileSerializer(profile).data

        return Response({
            "profile": serialized_profile,
            "token": auth_token
        }, status=status.HTTP_201_CREATED)


class ProfileViewSet(ViewSet):
    permission_classes = [IsProfileOwnerOrReadOnly]

    def retrieve(self, request: Request, pk: int = None):
        profile = get_profile_with_user(pk)
        serialized_profile = ProfileSerializer(profile).data

        return Response({
            "profile": serialized_profile
        }, status=status.HTTP_200_OK)

    def update(self, request: Request, pk: int = None):
        profile = get_profile_with_user(pk)
        self.check_object_permissions(request, profile)

        serializer = ProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ProfileManagerService(profile).update(**serializer.validated_data)

        serialized_profile = ProfileSerializer(profile).data

        return Response({
            "profile": serialized_profile
        }, status=status.HTTP_200_OK)

    def destroy(self, request: Request, pk: int = None):
        profile = get_profile_with_user(pk)
        self.check_object_permissions(request, profile)

        ProfileManagerService(profile).soft_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
