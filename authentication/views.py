from django.contrib.auth.models import User
from knox.views import LoginView as KnoxLoginView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from authentication.misc.custom_auth import CustomBasicAuthentication
from authentication.models import Profile
from authentication.permissions import IsProfileOwnerOrReadOnly
from authentication.selectors import get_profile, get_user_by_phone
from authentication.serializers import ProfileSerializer, SignUpRequestSerializer, VerificationRequestSerializer, PhoneSerializer
from authentication.services.profile import ProfileManagerService
from authentication.services.token_auth import SmsVerificationService
from authentication.utils import make_phone_uniform


MESSAGE_TEMPLATE = "Зубастый ректум приглашает вас, код {0}"


class LoginView(KnoxLoginView):
    authentication_classes = [CustomBasicAuthentication]


class ProfileVerificationView(APIView):
    def post(self, request, *args, **kwargs):
        # Пока использует только смс верификацию, потом добавим емыло
        serializer = VerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone: str = make_phone_uniform(serializer.validated_data.get("phone"))
        otp: str = serializer.validated_data.get("otp_code")
        user: User = get_user_by_phone(phone)
        profile: Profile = user.profile

        SmsVerificationService(user).verify_otp(otp)
        ProfileManagerService(profile).verify()

        return Response("verified successfully", status=status.HTTP_200_OK)


# class EmailResetPasswordInitView(APIView):
#     def post(self, request):
#         serializer = EmailSerializer(request.data)
#         serializer.is_valid(raise_exception=True)
#
#         email = serializer.validated_data.get("email")
#         user = get_object_or_404(User, email=email)
#
#         # Enter email verification service
#
#         return Response("verification code sent", status=status.HTTP_200_OK)


class SendVerificationCodeView(APIView):
    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone: str = make_phone_uniform(serializer.validated_data.get("phone"))
        user: User = get_user_by_phone(phone)

        SmsVerificationService(user).send_otp(message_template=MESSAGE_TEMPLATE)

        return Response("verification code sent", status=status.HTTP_200_OK)


# class ResetPasswordConfirmView(APIView):
#     def post(self, request):
#         serializer = VerificationRequestSerializer(request.data)
#         serializer.is_valid(raise_exception=True)
#
#         phone = make_phone_uniform(serializer.validated_data.get("phone"))
#         otp = serializer.validated_data.get("otp_code")
#         user = get_object_or_404(User, username=phone)
#
#         BaseVerificationService(user).verify_otp(otp)
#
#         return Response("verified successfully", status=status.HTTP_200_OK)
#
#
# class ResetPasswordDoneView(APIView):
#     def post(self, request):
#         pass


class SignUpView(APIView):
    def post(self, request):
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

    def retrieve(self, request, pk=None):
        profile: Profile = get_profile(pk)
        serialized_profile = ProfileSerializer(profile).data

        return Response({
            "profile": serialized_profile
        }, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        profile: Profile = get_profile(pk)
        self.check_object_permissions(request, profile)

        serializer = ProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ProfileManagerService(profile).update(**serializer.validated_data)

        serialized_profile = ProfileSerializer(profile).data

        return Response({
            "profile": serialized_profile
        }, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        profile: Profile = get_profile(pk)
        self.check_object_permissions(request, profile)

        ProfileManagerService(profile).soft_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


