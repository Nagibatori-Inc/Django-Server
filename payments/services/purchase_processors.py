import base64
import datetime

import requests
import structlog
from rest_framework.exceptions import ValidationError

from DjangoServer.settings import YOO_KASSA_ID, YOO_KASSA_SECRET
from payments.exceptions import PaymentError
from payments.models import Payment, PaymentStatus

logger = structlog.get_logger(__name__)

YOO_KASSA_STATUS_MAPPING = {
    "pending": PaymentStatus.PENDING,
    "waiting_for_capture": PaymentStatus.PENDING,
    "succeeded": PaymentStatus.SUCCESSFUL,
    "cancelled": PaymentStatus.CANCELLED,
}


class YooKassa:
    PAYMENT_URL = "https://api.yookassa.ru/v3/payments/"

    def __init__(self, payment: Payment):
        self.payment = payment
        self.headers = {
            "Idempotence-Key": str(payment.id),
            "Authorization": "Basic "
            + base64.b64encode(f"{YOO_KASSA_ID}:{YOO_KASSA_SECRET}".encode("ascii")).decode("ascii"),
            "Content-Type": "application/json",
        }

    def init_transaction(self):
        data = self.payment_to_format()

        try:
            response = requests.post(
                url=self.PAYMENT_URL,
                json=data,
                headers=self.headers,
            )
        except Exception as e:
            logger.error("Error during request to payment gateway", error=e)
            raise PaymentError(detail="Ошибка при отправке запроса в платежную систему")

        try:
            transaction_data = response.json()
            transaction_id = transaction_data["id"]
            confirm_url = transaction_data["confirmation"]["confirmation_url"]
        except Exception as e:
            logger.error("Error while parsing response from payment gateway", error=e)
            raise PaymentError(detail="Неверный формат ответа от платежной системы")

        self.payment.external_transaction_id = transaction_id
        self.payment.save(update_fields=["external_transaction_id"])

        return confirm_url

    def finalize_transaction(self, event_type: str, external_payment: dict):
        try:
            response = requests.get(
                url=self.PAYMENT_URL + external_payment["id"],
            )
            verified_transaction = response.json()
        except Exception as e:
            logger.error("Error during request for verification of transaction", error=e)
            raise PaymentError(detail="Ошибка при запросе на проверку транзакции")

        try:
            external_status = external_payment["status"]
            internal_status = YOO_KASSA_STATUS_MAPPING[external_status]
        except Exception as e:
            logger.error("Error during parsing of the webhook status", error=e)
            raise PaymentError(detail="Ошибка обработки вебхука")

        if verified_transaction["status"] != external_status:
            raise ValidationError("Транзакция невверна")

        self.payment.status = internal_status
        self.payment.completed_at = datetime.datetime.now()
        self.payment.save(update_fields=["status", "completed_at"])

    def payment_to_format(self):
        data = {
            "amount": {"value": str(self.payment.amount), "currency": "RUB"},
            "capture": True,
            "confirmation": {"type": "redirect", "return_url": "https://www.example.com/return_url"},
        }

        return data
