import enum
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.models import DO_NOTHING

import booking.models


class Providers(enum.StrEnum):
    YOO_KASSA = "YOO_KASSA"


class PaymentStatus(enum.StrEnum):
    PENDING = "PND"
    CANCELLED = "CAN"
    SUCCESSFUL = "SUC"
    ERROR = "ERR"


# Create your models here.
class Payment(models.Model):
    providers = ((Providers.YOO_KASSA, "ЮКасса"),)

    statuses = (
        (PaymentStatus.ERROR, "ошибка"),
        (PaymentStatus.PENDING, "в процессе"),
        (PaymentStatus.SUCCESSFUL, "успешен"),
        (PaymentStatus.CANCELLED, "отменен"),
    )

    id = models.UUIDField(
        unique=True,
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
    )
    user = models.ForeignKey(
        User,
        related_name="payments",
        verbose_name="Пользователь",
        on_delete=DO_NOTHING,
    )
    advert = models.ForeignKey(
        booking.models.Advert,
        related_name="promotion_payments",
        verbose_name="Объявление",
        on_delete=DO_NOTHING,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Стоимость",
    )
    external_transaction_id = models.CharField(
        max_length=128,
        verbose_name="ID внешней транзакции",
    )
    status = models.CharField(
        choices=statuses,
        max_length=16,
        verbose_name="Статус",
        default=PaymentStatus.PENDING,
    )
    service_provider = models.CharField(
        choices=providers,
        verbose_name="Провайдер",
        default=Providers.YOO_KASSA,
    )
    created_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Создано",
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Завершено",
    )

    def __str__(self):
        return f"Платеж [user={self.user}, advert={self.advert}]"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
