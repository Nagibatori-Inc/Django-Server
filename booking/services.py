from datetime import datetime
from typing import Type, Optional

import structlog
from django.db import transaction
from django.db.models import Subquery, IntegerField, Value, OuterRef, QuerySet
from django.db.models.functions import Coalesce
from rest_framework import status
from rest_framework.response import Response

from DjangoServer.helpers.datetime import renew_for_month
from DjangoServer.service import RestService
from authentication.models import Profile
from booking.models import Advert, AdvertStatus, Promotion, Boost, PromotionStatus
from booking.serializers import SearchFilterSerializer, AdvertSerializer, AdvertUpdateSerializer

logger = structlog.get_logger(__name__)

ADVERT_NOT_FOUND = Response(
    {'err_msg': 'Объявление не найдено'},
    status=status.HTTP_404_NOT_FOUND,
)
ADVERTS_NOT_FOUND = Response(
    {'err_msg': 'Объявления не найдены'},
    status=status.HTTP_404_NOT_FOUND,
)
PROMOTION_NOT_FOUND = Response({"err_msg": "Не указано объявление или пользователь"}, status=status.HTTP_404_NOT_FOUND)


class AdvertService(RestService):
    """
    Класс, реализующий бизнес логику работы с объявлениями

    Fields:
        + advert (Advert): Объявление

    Methods:
        + activate: Активирует объявление
        + deactivate: Деактивирует объявление
        + change: Изменение объявления (например, изменение описания)
        + find():
        + ranked_list():
        + advertise: Публикация объявления

    Properties:
        + advert(): Возвращает объект текущего объявления над которым производятся операции
    """

    def __init__(
        self, advert: Optional[Advert] = None, response: Optional[Response] = None, should_commit: bool = True
    ):
        super().__init__(response, should_commit)
        self.__advert = advert

    @property
    def advert(self) -> Optional[Advert]:
        return self.__advert

    @advert.setter
    def advert(self, advert: Optional[Advert]) -> None:
        self.__advert = advert

    @transaction.atomic
    def activate(self) -> 'AdvertService':
        if self.advert is None:
            self.not_found()
            return self

        self.advert.status = AdvertStatus.ACTIVE
        self.advert.activated_at = datetime.now()
        self.advert.save()
        return self

    @transaction.atomic
    def deactivate(self) -> 'AdvertService':
        if self.advert is None:
            self.not_found()
            return self

        self.advert.status = AdvertStatus.DISABLED
        self.advert.activated_at = None
        self.advert.save()
        return self

    @transaction.atomic
    def change(self, changed_data: AdvertUpdateSerializer) -> 'AdvertService':
        """
        Метод, изменения объявления по его идентификатору (первичному ключу) и профилю юзера, подавшего объявление
        По сути планируется применять когда юзер на веб аппе меняет поля объявления на соответствующей страничке ->
        тогда кидается запрос и в дело вступает этот метод

        :param changed_data (AdvertUpdateSerializer) Сериализованные данные объявления
        :return: AdvertService
        """
        if self.advert is None and self.response is None:
            self.not_found()
            return self

        self.advert = changed_data.save()
        return self

    @transaction.atomic
    def remove(self) -> 'AdvertService':
        advert: Optional[Advert] = self.advert
        if advert is None:
            self.not_found()
            return self

        self.advert = None
        advert.delete()
        return self

    @transaction.atomic
    def serialize(self, serializer: Type[AdvertSerializer]) -> 'AdvertService':  # type: ignore[override]
        serialized_advert = serializer(self.advert, many=False)
        self.ok(serialized_advert.data)

        logger.debug('serialized advert data', data=serialized_advert.data)

        return self

    @staticmethod
    def find(advert_pk: int, user_profile: Profile) -> 'AdvertService':
        """
        Метод, поиска объявления по его идентификатору (первичному ключу) и профилю юзера, подавшего объявление

        :param advert_pk (int) Идентификатор объявления-претендента к продвижению.
        :param user_profile (Profile) Профиль юзера, которому принадлежит объявление
        :return: AdvertService
        """
        advert: Optional[Advert] = Advert.objects.filter(id=advert_pk, contact=user_profile).first()

        if advert is None:
            return AdvertService().not_found()

        return AdvertService(advert).ok()

    @staticmethod
    @transaction.atomic
    def advertise(advert_serialized_data: AdvertSerializer, contact: Profile) -> 'AdvertService':
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
            validated_data['active_until'] = renew_for_month(datetime.now())

        return AdvertService(advert_serialized_data.save(contact=contact))

    def created(self) -> 'AdvertService':
        """
        Если объявление создано, возвращает `201 CREATED`

        :return: AdvertService
        """
        if self.response is None and self.advert:
            self.response = Response(status=status.HTTP_201_CREATED)

        return self

    def not_found(self) -> 'AdvertService':
        """
        Если объявления не найдены, возвращает `404 NOT FOUND`, иначе продолжает цепочку

        :return: RestService
        """
        if self.response is None and self.advert is None:
            self.response = ADVERT_NOT_FOUND

        return self


class AdvertsRecommendationService(RestService):
    def __init__(
        self,
        adverts: Optional[QuerySet[Advert]] = None,
        response: Optional[Response] = None,
        should_commit: bool = True,
    ):
        super().__init__(response, should_commit)
        self.__adverts = adverts

    @property
    def adverts(self) -> Optional[QuerySet[Advert]]:
        return self.__adverts

    def _get(self, pk: int, profile: Profile) -> AdvertService:
        advert: Optional[Advert] = AdvertService.find(advert_pk=pk, user_profile=profile).advert

        if advert and self.adverts and advert in self.adverts:
            return AdvertService(advert).ok()

        return AdvertService().not_found()

    @transaction.atomic
    def serialize(self, serializer: Type[AdvertSerializer]):  # type: ignore[override]
        if self.adverts is None:
            return self.not_found()

        serialized_queryset = serializer(self.adverts.values(), many=True)
        self.ok(serialized_queryset.data)

        logger.debug('serialized adverts queryset', data=serialized_queryset.data, response=self.response)

        return self

    @transaction.atomic
    def view_ad(self, pk: int, profile: Profile):
        return self._get(pk, profile)

    @staticmethod
    @transaction.atomic
    def list():
        queryset = Advert.objects.filter(status=AdvertStatus.ACTIVE)

        return AdvertsRecommendationService(queryset).ok()  # TODO: what the hack is this warnings?

    @staticmethod
    @transaction.atomic
    def ranked_list(filters: SearchFilterSerializer):
        valid_data = filters.validated_data
        queryset = (
            Advert.objects.filter(
                **{
                    k: v
                    for k, v in {
                        'price__gte': valid_data.get('min_price', None),
                        'price__lte': valid_data.get('max_price', None),
                    }.items()
                    if v is not None
                },
                title__icontains=valid_data.get('title', ''),
                status=AdvertStatus.ACTIVE,
            )
            .annotate(
                promotion_rate=Coalesce(
                    Subquery(
                        Promotion.objects.filter(advert=OuterRef('pk')).values('rate')[:1], output_field=IntegerField()
                    ),
                    Value(0),
                )
            )
            .order_by('-promotion_rate', '-created_at')
        )

        if len(queryset) == 0 or queryset is None:
            return AdvertsRecommendationService().not_found()

        return AdvertsRecommendationService(queryset).ok()  # TODO: what the hack is this warnings?

    def not_found(self) -> 'AdvertsRecommendationService':
        """
        Если объявления не найдены, возвращает `404 NOT FOUND`, иначе продолжает цепочку

        :return: RestService
        """
        if self.response is None and self.adverts is None:
            self.response = ADVERTS_NOT_FOUND

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

    def __init__(
        self, promotion: Optional[Promotion] = None, response: Optional[Response] = None, should_commit: bool = True
    ):
        super().__init__(response, should_commit)
        self.__promotion = promotion

    @property
    def promotion(self) -> Optional[Promotion]:
        return self.__promotion

    @promotion.setter
    def promotion(self, promotion: Promotion) -> None:
        self.__promotion = promotion

    @transaction.atomic
    def boost(self, how_to_boost: Boost) -> 'PromotionService':
        promotion: Optional[Promotion] = self.promotion
        if promotion is None:
            self.not_found()
            return self

        promotion = how_to_boost.boost(promotion=promotion)
        promotion.save()  # type: ignore
        return self

    @transaction.atomic
    def disable(self) -> 'PromotionService':
        promotion = self.promotion
        if promotion is None:
            self.not_found()
            return self

        promotion.status = PromotionStatus.DISABLED
        promotion.save()
        return self

    @transaction.atomic
    def remove(self) -> 'PromotionService':
        promotion = self.promotion
        if promotion is None:
            self.not_found()
            return self

        self.promotion = None
        promotion.delete()
        return self

    @staticmethod
    def find(
        promotion_pk: int, advert: Optional[Advert] = None, user_profile: Optional[Profile] = None
    ) -> 'PromotionService':
        """
        Метод, поиска объявления по его идентификатору (первичному ключу) и профилю юзера, подавшего объявление

        :param promotion_pk (int) Идентификатор объекта продвижения
        :param advert (Advert) Объект модели объявления. Может быть None
        :param user_profile (Profile) Профиль юзера, которому принадлежит объявление. Может быть None
        :return: PromotionService
        """
        promotion: Optional[Promotion]

        if advert:
            promotion = Promotion.objects.filter(
                id=promotion_pk,
                advert=advert,
            ).first()

        elif user_profile:
            promotion = (
                Promotion.objects.filter(
                    id=promotion_pk,
                    advert__contact=user_profile,
                )
                .select_related('advert')
                .first()
            )

        else:
            return PromotionService().not_found()

        return PromotionService(promotion).ok()

    @staticmethod
    @transaction.atomic
    def promote(
        type: str,
        rate: int,
        advert: Optional[Advert] = None,
        advert_pk: Optional[int] = None,
        user_profile: Optional[Profile] = None,
    ) -> 'PromotionService':
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
                advert=AdvertService.find(advert_pk, user_profile),
            )

        else:
            return PromotionService().not_found()

        return PromotionService(promotion)

    def created(self) -> 'PromotionService':
        """
        Если продвижение объявления успешно создано, возвращает `201 CREATED`

        :return: PromotionService
        """
        if self.response is None and self.promotion:
            self.response = Response(status=status.HTTP_201_CREATED)

        return self

    def not_found(self) -> 'PromotionService':
        """
        Если продвижение не найдено, возвращает `404 NOT FOUND`, иначе продолжает цепочку

        :return: RestService
        """
        if self.response is None and self.promotion is None:
            self.response = PROMOTION_NOT_FOUND

        return self
