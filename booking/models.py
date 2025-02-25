from django.db import models

from authentication.models import Profile


class Promotion(models.Model):
    """
    Модель продвижения объявления

    Fields:
        + type (CharField): Тип продвижения
        + rate (IntegerField): Уровень продвижения
    """

    type = models.CharField(max_length=50)
    rate = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Продвижение"
        verbose_name_plural = "Продвижения"

    def __str__(self):
        return self.type


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
        default=None
    )
    phone = models.CharField(max_length=12, verbose_name='Телефон')
    promotion = models.OneToOneField(
        Promotion,
        on_delete=models.CASCADE,
        related_name='advert',
        verbose_name='Продвижение',
        null=True,
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True, # поле auto_now_add ставит datetime.now() когда объект только создан
        verbose_name='Создано'
    )
    activated_at = models.DateTimeField(
        auto_now=True, # поле auto_now задает значение datetime.now() когда у объект модели вызывает метод save()
        verbose_name='Активировано',
        null=True
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
    def is_active(self):
        return self.status == AdvertStatus.ACTIVE

    @property
    def is_promoted(self):
        return self.promotion
