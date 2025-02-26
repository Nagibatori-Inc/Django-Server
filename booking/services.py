from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from DjangoServer.decorators import handle_service_exceptions
from DjangoServer.service import RestService
from authentication.models import Profile
from booking.models import Advert, AdvertStatus, Promotion
from booking.serializers import SearchFilterSerializer


class AdvertService(RestService):
    """
    Класс, реализующий бизнес логику работы с объявлениями

    Fields:
        + advert (Advert): Объявление
    
    Methods:
        + activate: Активирует объявление
        + deactivate: Деактивирует объявление
        + change: изменение объявления (например, изменение описания)
        + find():
        + ranked_list():
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
    @handle_service_exceptions
    def activate(self):
        self.advert.status = AdvertStatus.ACTIVE
        self.advert.save()
        return self
        
    @transaction.atomic
    @handle_service_exceptions
    def deactivate(self):
        self.advert.status = AdvertStatus.DISABLED
        self.advert.save()
        return self
        
    @transaction.atomic
    @handle_service_exceptions
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
    @handle_service_exceptions
    def remove(self):
        advert: Advert = self.advert
        advert.delete()
        return self

    @staticmethod
    @handle_service_exceptions
    def find(advert_pk: int, user_profile: Profile):
        """
        Метод, поиска объявления по его идентификатору (первичному ключу) и профилю юзера, подавшего объявление

        :param advert_pk (int) Идентификатор объявления-претендента к продвижению.
        :param user_profile (Profile) Профиль юзера, которому принадлежит объявление
        :return: AdvertService
        """
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
    def ranked_list(filters: SearchFilterSerializer):
        pass

    @staticmethod
    @transaction.atomic
    @handle_service_exceptions
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

        :returns: AdvertService
        """
        advert: Advert = Advert.objects.create(
            title=title,
            description=description,
            price=price,
            contact=contact,
            phone=phone,
            promotion=promotion,
        )

        if promotion is None:
            PromotionService
        
        return AdvertService(advert)

    def created(self):
        """
        Если объявление создано, возвращает `201 CREATED`

        :return: AdvertService
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
        + find():
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

    @handle_service_exceptions
    def boost(self):
        return self

    @staticmethod
    @handle_service_exceptions
    def find(promotion_pk: int, advert: Advert = None, user_profile: Profile = None):
        """
        Метод, поиска объявления по его идентификатору (первичному ключу) и профилю юзера, подавшего объявление

        :param promotion_pk (int) Идентификатор объекта продвижения
        :param advert (Advert) Объект модели объявления. Может быть None
        :param user_profile (Profile) Профиль юзера, которому принадлежит объявление. Может быть None
        :return: PromotionService
        """
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
    @handle_service_exceptions
    def promote(
            type: str,
            rate: int,
            advert: Advert = None,
            advert_pk: int = None,
            user_profile: Profile = None,
    ):
        """
        Метод, реализующий логику подключения 'продвижения' полученному (переданному) объявлению

        :param type (str) Тип продвижения
        :param rate (int) Уровень продвижения
        :param advert (Advert) Объект модели объявления. Может быть None
        :param advert_pk (int) Идентификатор объявления-претендента к продвижению. Может быть None
        :param user_profile (Profile) Профиль юзера, которому принадлежит объявление. Может быть None

        TODO: Аналогично, любое продвижение объявления должно создаваться только этим методом

        :return: PromotionService
        """
        promotion: Promotion

        if advert:
            promotion = Promotion.objects.create(
                type=type,
                rate=rate,
                advert=advert,
            )

        elif user_profile and advert_pk:
            promotion = Promotion.objects.create(
                type=type,
                rate=rate,
                advert=AdvertService.find(
                    advert_pk,
                    user_profile
                ),
            )

        else:
            return PromotionService(
                Promotion(),
                response=Response(
                    {"err_msg": "Не указано объявление или пользователь"},
                    status=status.HTTP_404_NOT_FOUND
                ),
            )

        return PromotionService(promotion)

    def created(self):
        """
        Если продвижение объявления успешно создано, возвращает `201 CREATED`

        :return: PromotionService
        """
        if self.response is None and self.promotion:
            self.response = Response(status=status.HTTP_201_CREATED)

        return self

