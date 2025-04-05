from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound

from authentication.models import Profile, OneTimePassword


def get_profile_with_user(pk: int = None) -> Profile:
    try:
        profile = (Profile.objects.filter(is_deleted=False).select_related("user").get(pk=pk))
    except Profile.DoesNotExist:
        raise NotFound(detail={
            "detail": "profile not found"
        })
    return profile


def get_user_with_profile_by_phone(phone: str = None) -> User:
    try:
        user = (User.objects.filter(is_active=True).select_related("profile").get(username=phone))
    except User.DoesNotExist:
        raise NotFound(detail={
            "detail": "user not found"
        })
    return user


def get_otp_with_user_by_code(token_code: str = None) -> OneTimePassword:
    try:
        otp = OneTimePassword.objects.select_related("user").get(code=token_code)
    except OneTimePassword.DoesNotExist:
        raise NotFound(detail={"detail": "otp not found"})
    return otp
