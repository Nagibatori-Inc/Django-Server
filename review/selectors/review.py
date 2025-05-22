from django.db.models import QuerySet
from rest_framework.generics import get_object_or_404

from authentication.models import Profile
from review.models import Review


def get_visible_reviews(profile_id: int) -> QuerySet[Review]:
    """Получить все видимые на фронте отзывы профиля"""
    return Review.objects.filter(profile_id=profile_id, is_approved=True)


def get_review_author(review_id: int) -> Profile:
    """Получить автора отзыва по его айди"""
    return get_object_or_404(Review, id=review_id).author


def get_reviews_to_moderate() -> QuerySet[Review]:
    """Получить отзывы для модерирования"""
    return Review.objects.filter(is_approved=False)
