from smsaero import SmsAero
import structlog

from DjangoServer.settings import SMS_MODE, SMSAERO_API_KEY, SMSAERO_EMAIL
from notification.enums.sms import SmsMode

logger = structlog.get_logger(__name__)


class BaseSmsService:
    """
    Класс, ответственный за создание базового контракта рассылки СМС

    Methods:
        + send_message: Отсылает сообщение на указанный номер
    """

    def send_message(self, phone: str, text: str, **kwargs) -> dict:
        raise NotImplementedError("send_message() should be overridden in child classes")


class SmsAeroService(BaseSmsService):
    """
    Конкретная имплементация контракта BaseSmsService с помощью АПИ SmsAero.

    Methods:
        + send_message: Отсылает сообщение на указанный номер через АПИ SmsAero
    """

    def __init__(self, api_key: str, email: str):
        self.api = SmsAero(api_key=api_key, email=email)

    def send_message(self, phone: str, text: str, **kwargs) -> dict:
        phone_repr = int(phone)
        response = self.api.send_sms(number=phone_repr, text=text, **kwargs)

        return response


class SmsDebugService(BaseSmsService):
    """
    Класс имплементирующий контракт BaseSmsService с помощью какого-либо
    потока вывода, предназначен для тестового окружения.

    Methods:
        + send_message: Отсылает сообщение в поток вывода с указанными
    """

    def send_message(self, phone: str, text: str, **kwargs) -> dict:
        logger.info(f"Message with content '{text}' is sent to number {phone}")
        return {"status": "delivered", "message": text}


sms_service = (
    SmsDebugService()
    if SMS_MODE != SmsMode.PRODUCTION
    else SmsAeroService(api_key=SMSAERO_API_KEY, email=SMSAERO_EMAIL)
)
