import datetime
import secrets
import string

from django.contrib.auth.models import User
from django.utils import timezone
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

    PROFILE_TYPE_CHOICES = (("IND", "Частное лицо"), ("CMP", "Компания"))

    name = models.CharField(max_length=50, null=True, verbose_name="Имя профиля")
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE, verbose_name="Пользователь")
    type = models.CharField(max_length=3, choices=PROFILE_TYPE_CHOICES, default="IND", verbose_name="Тип профиля")
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")
    is_verified = models.BooleanField(default=False, verbose_name="Верифицирован")
    liked_adverts = models.ManyToManyField(
        to='booking.Advert',
        verbose_name='Понравившиеся объявления',
        related_name='users_likes',
        blank=True,
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Profile [name='{self.name}', user='{self.user}', type='{self.type}']"


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

    user = models.ForeignKey(User, related_name="otps", on_delete=models.CASCADE, verbose_name="Пользователь")
    code = models.CharField(max_length=128, default="", verbose_name="Одноразовый код (хэш)")
    creation_date = models.DateTimeField(auto_now=True, verbose_name="Время создания")

    def save(self, *args, **kwargs) -> str:  # type: ignore
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

    has_expired.fget.short_description = "OTP уже истек"  # type: ignore

    class Meta:
        verbose_name = "Одноразовый код"
        verbose_name_plural = "Одноразовые коды"
