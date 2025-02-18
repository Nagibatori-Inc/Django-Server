from django.db import models
from django.urls import reverse


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

    def get_absolute_url(self):
        return reverse("Propmotion_detail", kwargs={"pk": self.pk})


class Advert(models.Model):
    """
    Модель объявления об аренде спецтехники
    
    :Fields:
    - category (Category): Категория объявления
    - subcategory (Subcategory): Подкатегория 
    + title (CharField): Название объявления
    + description (TextField): Текст объявления
    + price (DecimalField): Стоимость услуги
    - contact (Profile | Новая моделька о правовых Субъектах): Контакты - контактное лицо
    + phone (Profile, но пока просто CharField): Контакты - телефон
    + created_at (DateTimeField): Дата, когда было создано объявление
    + activated_at (DateTimeField): Дата, когда пользователь активировал свое объявление
    + is_active (BooleanField): Активно ли объявление
    + promotion (Promotion): Данные о продвижении объявления
    """
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=11, 
        decimal_places=2
    )
    phone = models.CharField(length=12)
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name='advert',
        verbose_name='Объявление',
        null=True,
    )
    
    created_at = models.DateTimeField(auto_now_add=True) # поле auto_now_add ставит datetime.now() когда объект только создан
    activated_at = models.DateTimeField(
        auto_now=True, # поле auto_now задает значение datetime.now() когда у объект модели вызывает метод save()
        null=True
    ) 
    is_active = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        
    def __str__(self):
        return self.title

    @property
    def is_promoted(self):
        return self.promotion
