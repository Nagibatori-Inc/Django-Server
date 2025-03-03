from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound

from authentication.models import Profile


def get_profile(pk: int = None) -> Profile:
    try:
        profile: Profile = (Profile
                            .objects
                            .filter(is_deleted=False)
                            .select_related("user").get(pk=pk))

    except Profile.DoesNotExist:
        raise NotFound(detail={
            "detail": "profile not found"
        })
    return profile


def get_user_by_phone(phone: str = None):
    try:
        user: User = (User
                      .objects
                      .filter(is_active=True)
                      .select_related("profile").get(username=phone))

    except User.DoesNotExist:
        raise NotFound(detail={
            "detail": "user not found"
        })
    return user
