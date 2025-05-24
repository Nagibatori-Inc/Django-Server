import pytest

from authentication.models import Profile
from review.models import Review
from review.tests.factories import ReviewFactory


def save_profile_object(profile: Profile) -> None:
    """Сохранить в бд объект профиля, созданный фикстурой"""
    profile.user.save()
    profile.save()


def save_review_object(review: Review) -> None:
    """Сохранить в бд объект отзыва, созданный фикстурой"""
    save_profile_object(profile=review.profile)
    save_profile_object(profile=review.author)
    review.save()


@pytest.fixture
def review() -> Review:
    """Фикстура модели отзыва"""
    return ReviewFactory()
