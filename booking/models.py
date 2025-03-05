from typing import Dict, Optional

from django.db import models

from authentication.models import Profile


class PromotionStatus:
    ACTIVE = 'ACTIVE'
    DISABLED = 'DISABLED'


class Promotion(models.Model):
    """
    Модель продвижения объявления

    Fields:
        + type (CharField): Тип продвижения
        + rate (IntegerField): Уровень продвижения
    """
    PROMOTION_STATUS_CHOICES = (
        (PromotionStatus.ACTIVE, 'Активно'),
        (PromotionStatus.DISABLED, 'Отключено'),
    )

    type = models.CharField(max_length=50, verbose_name='Тип | Описание продвижения')
    rate = models.IntegerField(default=0, verbose_name='Уровень продвижения')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано",
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=16,
        choices=PROMOTION_STATUS_CHOICES,
        default=PromotionStatus.DISABLED,
        verbose_name="Статус",
    )
    class Meta:
        verbose_name = "Продвижение"
        verbose_name_plural = "Продвижения"

    def __str__(self):
        return self.type
    
    @property
    def is_active(self) -> bool:
        return self.status == PromotionStatus.ACTIVE
    
    
class BoostType:
    INCREASE = 'increase'
    SET_ANOTHER = 'set_another'

    
class Boost:
    """
    Буста продвижения конкретного объявления

    Fields:
        + boost_type (BoostType): Тип буста
    """
    def __init__(self, boost_type: BoostType, another: Optional[Dict[str, int]] = None):
        self._validate()
        self.boost_type = boost_type
        self.another = another
        
    def _validate(self):
        if self.another and len(self.another) != 1:
                raise ValueError('dictionary should have exactly have one pair of promotion`s type & rate')
        
    def increase(self, promotion: Promotion):
        promotion.rate += 1
        
    def set_another(self, promotion: Promotion):
        promotion.type = list(self.another.keys())[0]
        promotion.rate = list(self.another.values())[0]
    
    def boost(self, promotion: Promotion):
        if self.boost_type == BoostType.INCREASE:
            self.increase(promotion)
        elif self.boost_type == BoostType.SET_ANOTHER:
            self.set_another(promotion)
            
        return promotion


class AdvertStatus:
    ACTIVE = 'ACTIVE'
    DISABLED = 'DISABLED'


class Advert(models.Model):
    """
    Модель объявления об аренде спецтехники
    
    Fields:
        - category (Category): Категория объявления
        - subcategory (Subcategory): Подкатегория
        + title (CharField): Название объявления
        + description (TextField): Текст объявления
        + price (DecimalField): Стоимость услуги
        + contact (Profile | Новая моделька о правовых Субъектах): Контакты - контактное лицо
        + phone (Profile, но пока просто CharField): Контакты - телефон
        + created_at (DateTimeField): Дата, когда было создано объявление
        + activated_at (DateTimeField): Дата, когда пользователь активировал свое объявление
        + status (CharField): Статус объявления. Принимает два значения: ACTIVE или DISABLED
        + promotion (Promotion): Данные о продвижении объявления

    Properties:
        + is_active(): возвращает True, если статус объявления ACTIVE (то есть активно)
        + is_promoted(): возвращает True, если у объявление активировано 'Продвижение'
    """
    ADVERT_STATUS_CHOICES = (
        (AdvertStatus.ACTIVE, 'Активировано'),
        (AdvertStatus.DISABLED, 'Не опубликовано'),
    )

    title = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(
        max_digits=11, 
        decimal_places=2,
        verbose_name='Стоимость'
    )
    contact = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='adverts',
        verbose_name='Контактное лицо',
        default=None,
        blank=True,
    )
    phone = models.CharField(max_length=12, verbose_name='Телефон')
    promotion = models.OneToOneField(
        Promotion,
        on_delete=models.CASCADE,
        related_name='advert',
        verbose_name='Продвижение',
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True, # поле auto_now_add ставит datetime.now() когда объект только создан
        verbose_name='Создано'
    )
    activated_at = models.DateTimeField(
        verbose_name='Активировано',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=16,
        choices=ADVERT_STATUS_CHOICES,
        default=AdvertStatus.DISABLED,
        verbose_name='Статус'
    )
    
    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        
    def __str__(self):
        return self.title

    @property
    def is_active(self) -> bool:
        return self.status == AdvertStatus.ACTIVE

    @property
    def is_promoted(self) -> bool:
        return self.promotion is not None
