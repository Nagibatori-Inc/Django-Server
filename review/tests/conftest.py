from authentication.models import Profile
from review.models import Review


def save_profile_object(profile: Profile) -> None:
    """Сохранить в бд объект профиля, созданный фикстурой"""
    profile.user.save()
    profile.save()


def save_review_object(review: Review) -> None:
    """Сохранить в бд объект отзыва, созданный фикстурой"""
    save_profile_object(profile=review.profile)
    save_profile_object(profile=review.author)
    review.save()
