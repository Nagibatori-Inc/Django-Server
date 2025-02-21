from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password as compare_otps
from django.http import Http404
from knox.models import AuthToken
from knox.views import LoginView as KnowLoginView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from DjangoServer.settings import SMS_SERVICE
from authentication.custom_auth import CustomBasicAuthentication
from authentication.models import Profile
from authentication.permissions import IsProfileOwnerOrReadOnly
from authentication.serializers import ProfileSerializer, SignUpRequestSerializer
from authentication.utils import make_phone_uniform

sms_service = SMS_SERVICE


class OTPVerificationView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.data:
            return Response({"err_msg": "no data was sent"}, status=status.HTTP_400_BAD_REQUEST)

        otp_code = request.data.get("otp", None)
        phone = request.data.get("phone", None)

        if not otp_code or not phone:
            return Response(
                {"err_msg": "otp code and phone number are both required"},
                status=status.HTTP_400_BAD_REQUEST)

        phone = make_phone_uniform(phone)
        user = get_user_model().objects.get(username=phone)

        if user.profile.is_verified:
            return Response(
                {"err_msg": "user already verified"},
                status=status.HTTP_400_BAD_REQUEST)

        latest_otp = user.otps.latest("creation_date")

        if latest_otp.has_expired:
            return Response(
                {"err_msg": "otp has been invalidated"},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_valid = compare_otps(otp_code, latest_otp.code)

        if otp_valid:
            user.profile.is_verified = True
            user.profile.save(update_fields=["is_verified"])
            return Response({"detail": "user verified successfully"}, status=status.HTTP_200_OK)

        return Response({"err_msg": "otps doesn't match"}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(KnowLoginView):
    authentication_classes = [CustomBasicAuthentication]


class SignUpView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.data:
            return Response({"err_msg": "no data was sent"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SignUpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile, otp_code = serializer.save()
        auth_token = AuthToken.objects.create(profile.user)[1]

        print(otp_code)

        return Response({
            "profile": ProfileSerializer(profile).data,
            "token": auth_token
        }, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsProfileOwnerOrReadOnly]

    def get_profile(self, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist as ex:
            raise Http404

        return profile

    def get(self, request, *args, **kwargs):
        profile_id = kwargs["pk"]
        profile = self.get_profile(profile_id)

        return Response(ProfileSerializer(profile).data, status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        profile_id = kwargs["pk"]
        profile = self.get_profile(pk=profile_id)
        self.check_object_permissions(request, profile)

        new_profile_data = request.data
        if not new_profile_data:
            return Response({"err_msg": "no data was sent"}, status=status.HTTP_400_BAD_REQUEST)

        updated_profile = ProfileSerializer(profile, data=new_profile_data)
        updated_profile.is_valid(raise_exception=True)
        updated_profile.save()

        return Response(updated_profile.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        profile_id = kwargs["pk"]
        profile = self.get_profile(profile_id)
        self.check_object_permissions(request, profile)
        # TODO set user to inactive as well
        profile.is_deleted = True
        profile.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
