from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import check_password as compare_otps

from DjangoServer.settings import SMS_MODE, SMSAERO_API_KEY, SMSAERO_EMAIL
from authentication.models import OneTimePassword
from authentication.services.sms import BaseSmsService, SmsAeroService, SmsDebugService


class BaseVerificationService:
    """
    Сервис, отвечающий за верификацию пользователя

    Methods:
        + verify:
    """
    def __init__(self, user: User):
        self.user = user

    def _get_latest_otp(self) -> OneTimePassword:
        try:
            latest_otp = self.user.otps.latest("creation_date")
        except OneTimePassword.DoesNotExist:
            raise ValidationError(detail={"detail": "user doesn't have any codes"})
        return latest_otp

    def _validate_otp(self, otp: str) -> None:
        latest_otp = self._get_latest_otp()

        if latest_otp.has_expired:
            raise ValidationError(detail={"detail": "latest otp already expired"})

        otp_valid = compare_otps(otp, latest_otp.code)

        if not otp_valid:
            raise ValidationError(detail={"detail": "otp doesn't match"})

    def create_otp(self) -> str:
        otp = OneTimePassword(user=self.user).save()
        return otp

    def verify_otp(self, otp: str) -> None:
        self._validate_otp(otp)
