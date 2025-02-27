from django.contrib.auth.models import User
from knox.views import LoginView as KnoxLoginView
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from DjangoServer.settings import SMS_MODE, SMSAERO_API_KEY, SMSAERO_EMAIL
from authentication.misc.custom_auth import CustomBasicAuthentication
from authentication.models import Profile
from authentication.permissions import IsProfileOwnerOrReadOnly
from authentication.serializers import ProfileSerializer, SignUpRequestSerializer, VerificationRequestSerializer, \
    PhonePasswordResetInitSerializer
from authentication.services.profile import ProfileManagerService
from authentication.services.sms import SmsAeroService
from authentication.services.token_auth import SmsVerificationService
from authentication.utils import make_phone_uniform

sms_service = None
if SMS_MODE == "production":
    sms_service = SmsAeroService(api_key=SMSAERO_API_KEY, email=SMSAERO_EMAIL)


class ProfileVerificationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = make_phone_uniform(serializer.validated_data.get("phone"))
        otp = serializer.validated_data.get("otp_code")
        user = get_object_or_404(User, username=phone)

        SmsVerificationService(user).verify_otp(otp)
        ProfileManagerService(user.profile).verify()

        return Response("verified successfully", status=status.HTTP_200_OK)


class LoginView(KnoxLoginView):
    authentication_classes = [CustomBasicAuthentication]


class EmailResetPasswordInitView(APIView):
    def post(self, request):
        pass


class PhoneResetPasswordInitView(APIView):
    def post(self, request):
        serializer = PhonePasswordResetInitSerializer(request.data)
        serializer.is_valid(raise_exception=True)

        phone = make_phone_uniform(serializer.validated_data.get("phone"))
        user = get_object_or_404(User, username=phone)

        SmsVerificationService(user, sms_service).send_otp()

        return Response("Verification code sent", status=status.HTTP_200_OK)


class ResetPasswordConfirmView(APIView)
    def post(self, request):
        pass

class ResetPasswordDoneView(APIView):
    def post(self, request):
        pass


class ProfileViewSet(ViewSet):
    permission_classes = [IsProfileOwnerOrReadOnly]

    def create(self, request):
        serializer = SignUpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_token, profile = ProfileManagerService.create(**serializer.validated_data)
        SmsVerificationService(profile.user, sms_service).send_otp()

        return Response({
            "profile": ProfileSerializer(profile).data,
            "token": auth_token[1]
        }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        profile = get_object_or_404(Profile, pk=pk)
        return Response(ProfileSerializer(profile).data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        profile = get_object_or_404(Profile, pk=pk)
        self.check_object_permissions(request, profile)

        serializer = ProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ProfileManagerService(profile).update(**serializer.validated_data)

        return Response({
            "profile": ProfileSerializer(profile).data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        profile = get_object_or_404(Profile, pk=pk)
        self.check_object_permissions(request, profile)

        ProfileManagerService(profile).soft_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


