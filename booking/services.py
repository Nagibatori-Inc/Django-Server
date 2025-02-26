from datetime import datetime

from django.db import transaction
from django.db.models import Subquery, IntegerField, Value, OuterRef
from django.db.models.functions import Coalesce
from rest_framework import status
from rest_framework.response import Response

from DjangoServer.service import RestService
from authentication.models import Profile
from booking.models import Advert, AdvertStatus, Promotion
from booking.serializers import SearchFilterSerializer, AdvertSerializer


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
    def activate(self):
        self.advert.status = AdvertStatus.ACTIVE
        self.advert.activated_at = datetime.now()
        self.advert.save()
        return self
        
    @transaction.atomic
    def deactivate(self):
        self.advert.status = AdvertStatus.DISABLED
        self.advert.activated_at = None
        self.advert.save()
        return self
        
    @transaction.atomic
    def change(self, changed_data: AdvertSerializer):
        """
        Метод, поиска объявления по его идентификатору (первичному ключу) и профилю юзера, подавшего объявление

        :param changed_data (AdvertSerializer) Сериализованные данные объявления
        :return: AdvertService
        """
        advert: Advert = self.advert
        validated_data = changed_data.validated_data
        
        advert.title = validated_data.get('title')
        advert.description = validated_data.get('description')
        advert.price = validated_data.get('price')
        advert.phone = validated_data.get('phone')
        advert.promotion = validated_data.get('promotion')
        advert.activated_at = validated_data.get('activated_at')
        
        advert.save()
        return self
        
    @transaction.atomic
    def remove(self):
        advert: Advert = self.advert
        advert.delete()
        return self

    @staticmethod
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
        valid_data = filters.validated_data
        queryset = (
            Advert.objects
            .filter(
                title__icontains=valid_data['title'],
                price=valid_data['price']
            )
            .annotate(
                promotion_rate=Coalesce(
                    Subquery(
                        Promotion.objects
                        .filter(advert=OuterRef('pk'))
                        .values('rate')[:1],
                        output_field=IntegerField()
                    ),
                    Value(0)
                )
            )
            .order_by('-promotion_rate', '-created_at')
            .values()
        )

        return queryset

    @staticmethod
    @transaction.atomic
    def advertise(advert_serialized_data: AdvertSerializer, contact: Profile):
        """
        Метод реализации логики подачи объявления (Публикация объявления)

        TODO: ВСЕ объявления должны публиковаться через этот метод

        :param advert_serialized_data (AdvertSerializer) Сериализованные данные объявления
        :param contact (Profile) Контакты - контактное лицо
        :returns: AdvertService
        """
        validated_data = advert_serialized_data.validated_data

        if validated_data.get('status') == AdvertStatus.ACTIVE:
            validated_data['activated_at'] = datetime.now()

        return AdvertService(
            Advert.objects.create(
                title=validated_data.get('title'),
                description=validated_data.get('description'),
                price=validated_data.get('price'),
                phone=validated_data.get('phone'),
                status=validated_data.get('status', AdvertStatus.DISABLED),
                activated_at=validated_data.get('activated_at', None),
                contact=contact,
            )
        )

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

    def boost(self):
        return self

    @staticmethod
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
    def promote(
            type: str,
            rate: int,
            advert: Advert = None,
            advert_pk: int = None,
            user_profile: Profile = None,
    ):
        """
        Метод, реализующий логику подключения 'продвижения' полученному (переданному) объявлению

        TODO: Аналогично, любое продвижение объявления должно создаваться только этим методом

        :param type (str) Тип продвижения
        :param rate (int) Уровень продвижения
        :param advert (Advert) Объект модели объявления. Может быть None
        :param advert_pk (int) Идентификатор объявления-претендента к продвижению. Может быть None
        :param user_profile (Profile) Профиль юзера, которому принадлежит объявление. Может быть None
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

