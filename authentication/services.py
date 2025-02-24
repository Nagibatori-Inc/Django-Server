import smsaero
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password as compare_otps
from django.db import transaction
from knox.models import AuthToken
from rest_framework.exceptions import ParseError


from DjangoServer.settings import SMSAERO_EMAIL, SMSAERO_API_KEY, SMS_MODE
from authentication.models import OneTimePassword, Profile
from authentication.utils import make_phone_uniform


class VerificationService:
    # for now use parse error
    @staticmethod
    def verify(user, otp):
        try:
            latest_otp = user.otps.latest("creation_date")
        except OneTimePassword.DoesNotExist:
            raise ParseError(detail={"err_msg": "no otps for user"})

        if latest_otp.has_expired:
            raise ParseError(detail={"err_msg": "otp expired"})

        print(otp)
        otp_valid = compare_otps(otp, latest_otp.code)

        if not otp_valid:
            raise ParseError(detail={"err_msg": "invalid otp"})

        user.profile.is_verified = True
        user.profile.save(update_fields=["is_verified"])
        return


class BaseRegistrationService:
    def _send_code(self, otp, user):
        raise NotImplementedError(".send_code() must be overridden")

    def __create_user(self, user_data):
        phone = user_data.get("phone", None)
        password = user_data.get("password", None)
        first_name = user_data.get("first_name", None)
        email = user_data.get("email", None)

        phone = make_phone_uniform(phone)
        user_model = get_user_model()
        user = user_model(username=phone, first_name=first_name, email=email)
        user.set_password(raw_password=password)
        user.save()
        return user

    def __create_profile(self, user, user_data):
        profile_name = user_data.get("profile_name", None)
        type = user_data.get("type", None)
        profile = Profile.objects.create(user=user, name=profile_name, type=type)
        return profile

    @transaction.atomic
    def register(self, user_data):
        user = self.__create_user(user_data)
        profile = self.__create_profile(user, user_data)
        otp = OneTimePassword(user=user).save()
        auth_token = AuthToken.objects.create(profile.user)[1]
        self._send_code(otp, user)
        return profile, auth_token


class SmsRegistrationService(BaseRegistrationService):
    sms_service = smsaero.SmsAero(email=SMSAERO_EMAIL, api_key=SMSAERO_API_KEY) if SMS_MODE != "debug" else None

    def _send_code(self, otp, user):
        if SMS_MODE == "production":
            self.sms_service.send_sms(int(user.username), f"Тестовая рассылка - {otp}")
        elif SMS_MODE == "debug":
            print(otp)


class EmailRegistrationService(BaseRegistrationService):
    def _send_code(self, otp, user):
        pass
