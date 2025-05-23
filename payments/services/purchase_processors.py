import requests

from DjangoServer.settings import YOO_KASSA_ID, YOO_KASSA_SECRET
from payments.exceptions import PaymentError
from payments.models import Payment, PaymentStatus

YOO_KASSA_STATUS_MAPPING = {
    "pending": PaymentStatus.PENDING,
    "waiting_for_capture": PaymentStatus.PENDING,
    "succeeded": PaymentStatus.SUCCESSFUL,
    "cancelled": PaymentStatus.CANCELLED,
}


class YooKassa:
    PAYMENT_URL = "https://api.yookassa.ru/v3/payments"

    def __init__(self, payment: Payment):
        self.payment = payment
        self.headers = {"Idempotence-Key": payment.id, "Authorization": f"{YOO_KASSA_ID}:{YOO_KASSA_SECRET}"}

    def init_transaction(self):
        data = self.payment_to_format()

        try:
            response = requests.post(
                url=self.PAYMENT_URL,
                data=data,
                headers=self.headers,
            )
        except Exception:
            raise PaymentError()

        try:
            transaction_data = response.json()
            transaction_id = transaction_data["id"]
            confirm_url = transaction_data["confirmation"]["confirmation_url"]
        except Exception:
            raise PaymentError()

        self.payment.objects.update(external_transaction_id=transaction_id)

        return confirm_url

    def finalize_transaction(self, event_type: str, external_payment: dict):
        external_status = external_payment["status"]
        internal_status = YOO_KASSA_STATUS_MAPPING[external_status]

        self.payment.objects.update(status=internal_status)

    def payment_to_format(self):
        data = {
            "amount": {"value": self.payment.amount, "currency": "RUB"},
            "capture": "true",
            "confirmation": {"type": "redirect", "return_url": ""},
        }

        return data
