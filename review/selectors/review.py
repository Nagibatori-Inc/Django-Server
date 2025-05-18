from django.db.models import QuerySet

from review.models import Review


def get_visible_reviews(profile_id: int) -> QuerySet[Review]:
    """Получить все видимые на фронте отзывы профиля"""
    return Review.objects.filter(profile_id=profile_id, is_approved=True)
