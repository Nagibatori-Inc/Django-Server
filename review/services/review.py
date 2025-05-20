from rest_framework.generics import get_object_or_404

from review.models import Review


def delete_review_by_id(review_id: int) -> None:
    """
    Удаление отзыва с id=review_id
    :param review_id: id отзыва
    """
    review = get_object_or_404(Review, id=review_id)
    review.delete()
