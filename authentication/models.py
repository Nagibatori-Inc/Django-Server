import datetime
import secrets
import string

from django.utils import timezone
from django.conf import settings
from django.db import models
from django.contrib.auth.hashers import make_password as hash_value

from DjangoServer.settings import OTP_TTL


# Create your models here.
class Profile(models.Model):
    """
    Модель представляющая профиль пользователя

    Fields:
    + name (NULLABLE): Имя профиля, отображающееся в объявлениях, чатах, ЛК
    + user: Связь с User'ом, который используется для аутентификации и авторизации
    + type: Тип аккаунта, к примеру: Частное лицо или Компания
    + is_deleted: Поле soft delete'a, выставляется на True в случае удаления со стороны пользователя
    """

    PROFILE_TYPE_CHOICES = {
        "IND": "Частное лицо",
        "CMP": "Компания"
    }

    name = models.CharField(max_length=50, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="profile", on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=PROFILE_TYPE_CHOICES, default="IND")
    is_deleted = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)


class OneTimePassword(models.Model):
    """
    Одноразовый код для верификации

    Fields:
    + user: Связь с User'ом, которому был назначен и отослан код
    + code: Хэшированный 6-ти значный код
    + creation_date: Дата создания кода

    Properties:
    + has_expired(): Проверка истекла ли валидность кода
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="otps", on_delete=models.CASCADE)
    code = models.CharField(max_length=128, default="")
    creation_date = models.DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs) -> str:
        otp = ""
        if not self.code:
            otp = OneTimePassword.generate_otp()
            self.code = hash_value(otp)
        super().save(*args, **kwargs)
        return otp

    @staticmethod
    def generate_otp() -> str:
        digits = string.digits
        otp = ''.join(secrets.choice(digits) for _ in range(6))
        return otp

    @property
    def has_expired(self) -> bool:
        if self.creation_date + datetime.timedelta(minutes=OTP_TTL) <= timezone.now():
            return True
        return False

