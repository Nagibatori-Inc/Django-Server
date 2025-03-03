from typing import Dict

from smsaero import SmsAero


class BaseSmsService:
    """
    Класс, ответственный за создание базового контракта рассылки СМС

    Methods:
        + send_message: Отсылает сообщение на указанный номер
    """

    def send_message(self, phone: str, text: str, **kwargs) -> Dict:
        raise NotImplementedError("send_message() should be overridden in child classes")


class SmsAeroService(BaseSmsService):
    """
    Конкретная имплементация контракта BaseSmsService с помощью АПИ SmsAero.

    Methods:
        + send_message: Отсылает сообщение на указанный номер через АПИ SmsAero
    """

    def __init__(self, api_key: str, email: str):
        self.api = SmsAero(api_key=api_key, email=email)

    def send_message(self, phone: str, text: str, **kwargs) -> Dict:
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

    def send_message(self, phone: str, text: str, **kwargs) -> Dict:
        print(text)
        return {
            "status": "delivered",
            "message": text
        }
