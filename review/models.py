from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Review(models.Model):
    """Класс модели отзыва на профиль"""

    profile = models.ForeignKey(
        to='authentication.Profile',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Профиль, на который оставлен отзыв',
    )
    author = models.ForeignKey(
        to='authentication.Profile',
        on_delete=models.CASCADE,
        related_name='sent_reviews',
        verbose_name='Автор отзыва',
    )
    text = models.CharField(max_length=3000, blank=True, default='', verbose_name='Текст отзыва')
    rate = models.PositiveSmallIntegerField(
        verbose_name='Оценка от 1 до 5',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')

    is_approved = models.BooleanField(default=False, verbose_name='Одобрен модерацией')
    approved_by = models.ForeignKey(
        to='authentication.Profile',
        on_delete=models.SET_NULL,
        related_name='reviewed_by',
        null=True,
        blank=True,
        verbose_name='Одобривший модератор',
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'Отзыв от {self.author.name} на профиль {self.profile.name}'
