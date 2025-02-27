from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import check_password as compare_otps

from authentication.models import OneTimePassword
from authentication.services.sms import BaseSmsService


class BaseVerificationService:
    """
    Сервис, отвечающий за верификацию пользователя

    Methods:
        + verify: При условии действительности пользователя, ставит в профиле поле is_verified = True
    """
    def __init__(self, user: User):
        self.user = user

    def _validate_user(self) -> None:
        if self.user.profile.is_verified:
            raise ValidationError(detail={"detail": "user already verified"})

    def _validate_otp(self, otp: str) -> None:
        try:
            latest_otp = self.user.otps.latest("creation_date")
        except OneTimePassword.DoesNotExist:
            raise ValidationError(detail={"detail": "user doesn't have any codes"})

        if latest_otp.has_expired:
            raise ValidationError(detail={"detail": "latest otp already expired"})

        otp_valid = compare_otps(otp, latest_otp.code)

        if not otp_valid:
            raise ValidationError(detail={"detail": "otp doesn't match"})

    def _create_otp(self) -> str:
        otp = OneTimePassword(user=self.user).save()
        return otp

    def send_otp(self):
        raise NotImplementedError("Should be implemented in children classes")

    def verify_otp(self, otp: str) -> bool:
        self._validate_user()
        self._validate_otp(otp)

        return True


class SmsVerificationService(BaseVerificationService):
    # Ugly, but will stay for now
    def __init__(self, user: User, sms_service: BaseSmsService = None):
        super().__init__(user)
        self._sms_service = sms_service

    def send_otp(self):
        if self._sms_service is None:
            raise AttributeError("No sms_service was provided")

        otp = self._create_otp()
        self._sms_service.send_message(self.user.username, otp)

