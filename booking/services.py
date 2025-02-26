from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from DjangoServer.service import RestService
from authentication.models import Profile
from booking.models import Advert, AdvertStatus, Promotion


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
    
    def __init__(self, advert: Advert, response: Response = None, should_commit: bool = True):
        super().__init__(response, should_commit)
        self.__advert = advert

    @property
    def advert(self):
        return self.__advert
        
    @transaction.atomic
    def activate(self):
        self.advert.status = AdvertStatus.ACTIVE
        self.advert.save()
        return self
        
    @transaction.atomic
    def deactivate(self):
        self.advert.status = AdvertStatus.DISABLED
        self.advert.save()
        return self
        
    @transaction.atomic
    def change(self, changed_data: dict): # changed_data пока имеет тип dict, в дальнейшем будет объектом валидационной схемы
        advert: Advert = self.advert
        
        advert.title = changed_data['title']
        advert.description = changed_data['description']
        advert.price = changed_data['price']
        advert.phone = changed_data['phone']
        advert.promotion = changed_data['promotion']
        advert.activated_at = changed_data['activated_at']
        
        advert.save()
        return self
        
    @transaction.atomic
    def remove(self):
        advert: Advert = self.advert
        advert.delete()
        return self

    @staticmethod
    def find(advert_pk: int, user_profile: Profile):
        advert: Advert = (
            Advert.objects
            .filter(
                id=advert_pk,
                contact=user_profile
            )
            .first()
        )

        return AdvertService(advert).ok()

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

        TODO: ВСЕ объявления должны публиковаться через этот метод

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

    def created(self):
        """
        Если объявление создано, возвращает `201 CREATED`

        :return: Response | AdvertService
        """
        if self.response is None and self.advert:
            self.response = Response(status=status.HTTP_201_CREATED)

        return self


class PromotionService(RestService):
    """
    Класс, реализующий бизнес логику работы с моделью продвижения объявления

    Fields:
        + promotion (Promotion): Продвижение

    Methods:
        + boost(): Повысить уровень продвижения объявления
        + promote(): Продвинуть объявление
    """

    def __init__(self, promotion: Promotion, response: Response = None, should_commit: bool = True):
        super().__init__(response, should_commit)
        self.__promotion = promotion

    @property
    def promotion(self):
        return self.__promotion

    @promotion.setter
    def promotion(self, promotion: Promotion):
        self.__promotion = promotion

    def boost(self):
        return self

    @staticmethod
    def find(promotion_pk: int, advert: Advert = None, user_profile: Profile = None):
        promotion: Promotion
        
        if advert:
            promotion = (
                Promotion.objects
               .filter(
                    id=promotion_pk,
                    advert=advert,
                )
               .first()
            )
        
        elif user_profile:
            promotion = (
                Promotion.objects
               .filter(
                    id=promotion_pk,
                    advert=(
                        AdvertService
                        .find(
                            Promotion.objects
                            .get(id=promotion_pk)
                            .advert
                            .id,
                            user_profile
                        )
                        .advert
                    )
                )
               .first()
            )
            
        else:
            return PromotionService(
                Promotion(),
                response=Response(
                    { "err_msg": "Не указано объявление или пользователь" },
                    status=status.HTTP_404_NOT_FOUND
                ),
            )
            
        return (
            PromotionService(
                promotion
            )
            .ok()
        )

    @staticmethod
    @transaction.atomic
    def promote():
        """
        Метод, реализующий логику подключения 'продвижения' полученному (переданному) объявлению

        TODO: Аналогично, любое продвижение объявления должно создаваться только этим методом

        :return:
        """
        pass
