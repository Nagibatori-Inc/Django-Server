from django.db.models import Avg
from rest_framework.generics import get_object_or_404

from authentication.models import Profile
from review.models import Review


def delete_review_by_id(review_id: int) -> None:
    """
    Удаление отзыва с id=review_id
    :param review_id: id отзыва
    """
    review = get_object_or_404(Review, id=review_id)
    profile_id = review.profile_id  # type: ignore[attr-defined]
    review.delete()
    recalc_profile_rating(profile_id)


def recalc_profile_rating(profile_id: int) -> None:
    """
    Пересчитать рейтинг профиля, этот метод нужно вызывать при удалении/добавлении отзыва
    :param profile_id: id профиля, для которого нужно пересчитать рейтинг
    """
    new_rating = Review.objects.filter(is_approved=True).aggregate(Avg('rate'))['rate__avg']
    Profile.objects.filter(id=profile_id).update(rating=new_rating)


def moderate_review(review: Review, is_approved: bool) -> None:
    """Модерация отзыва"""
    if is_approved:
        Review.objects.filter(pk=review.pk).update(is_approved=is_approved)
    else:
        Review.objects.filter(pk=review.pk).delete()
    recalc_profile_rating(profile_id=review.profile.id)
