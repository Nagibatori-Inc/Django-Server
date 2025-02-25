from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from DjangoServer.service import RestService
from authentication.models import Profile
from booking.models import Advert, AdvertStatus


class AdvertService(RestService):
    """
    Класс, реализующий бизнес логику работы с объявлениями

    Fields:
        + advert (Advert): Объявление
    
    Methods:
        + activate: Активирует объявление
        + deactivate: Деактивирует объявление
        + change: изменение объявления (например, изменение описания)
        + advertise: Публикация объявления

    Properties:
        + advert(): Возвращает объект текущего объявления над которым производятся операции
    """
    
    def __init__(self, advert: Advert, response: Response = None):
        super().__init__(response)
        self.__advert = advert
        
    @transaction.atomic
    def activate(self) -> None:
        self.advert.status = AdvertStatus.ACTIVE
        self.advert.save()
        
    @transaction.atomic
    def deactivate(self) -> None:
        self.advert.status = AdvertStatus.DISABLED
        self.advert.save()
        
    @transaction.atomic
    def change(self, changed_data: dict) -> None: # changed_data пока имеет тип dict, в дальнейшем будет объектом валидационной схемы
        advert: Advert = self.advert
        
        advert.title = changed_data['title']
        advert.description = changed_data['description']
        advert.price = changed_data['price']
        advert.phone = changed_data['phone']
        advert.promotion = changed_data['promotion']
        advert.activated_at = changed_data['activated_at']
        
        advert.save()
        
    @transaction.atomic
    def remove(self) -> None:
        advert: Advert = self.advert
        advert.delete()

    def created(self):
        """
        Если объявление создано, возвращает `201 CREATED`

        :return: Response | AdvertService
        """
        if self.response is None and self.advert:
            self.response = Response(status=status.HTTP_201_CREATED)

        return self.__finalize_response()
        
    # TODO: ВСЕ объявления должны публиковаться через этот метод
    @staticmethod
    @transaction.atomic
    def advertise(
        title: str,
        description: str,
        price: float,
        contact: Profile,
        phone: str,
        promotion: str = None,
    ):
        """
        Метод реализации логики подачи объявления (Публикация объявления)

        :param title (str) Название объявления
        :param description (str) Текст объявления
        :param price (float) Стоимость услуги
        :param contact (Profile) Контакты - контактное лицо
        :param phone (str) Контакты - телефон
        :param promotion (str, optional) Данные о продвижении объявления. Может быть None

        Returns:
            AdvertService: объект сервисной логики работы с объявлениями
        """
        
        return AdvertService(
            Advert.objects.create(
                title=title,
                description=description,
                price=price,
                contact=contact,
                phone=phone,
                promotion=promotion,
            )
        )
        
    @property
    def advert(self):
        return self.__advert

    @property
    def response(self):
        return self.__response

    @response.setter
    def response(self, response: Response):
        self.__response = response
    