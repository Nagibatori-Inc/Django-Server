import datetime

from django.conf import settings
from django.db import models

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


class OneTimePassword(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="otps", on_delete=models.CASCADE)
    expiration_date = models.DateTimeField()

    @property
    def has_expired(self):
        if self.expiration_date + datetime.timedelta(minutes=OTP_TTL) <= datetime.datetime.now():
            return True
        return False

