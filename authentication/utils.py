from django.contrib.auth.models import User

from authentication.models import Profile


def make_phone_uniform(phone: str) -> str:
    """ Унификатор телефонного номера, приводит его к формату 71234567890"""
    if phone.startswith("+7"):
        return phone[1:]
    elif phone.startswith("+8"):
        return f"7{phone[2:]}"
    elif phone.startswith("8"):
        return f"7{phone[1:]}"
    return phone


def update_user(*, user: User, password: str, first_name: str, email: str, is_active: bool) -> None:
    user.first_name = first_name
    user.email = email
    user.is_active = is_active
    user.set_password(raw_password=password)
    user.save(update_fields=["first_name", "email", "password"])


def update_profile(*, profile: Profile, profile_name: str, profile_type: str, is_deleted: bool) -> None:
    profile.name = profile_name
    profile.type = profile_type
    profile.is_deleted = is_deleted
    profile.save(update_fields=["name", "type", "is_deleted"])


def create_user(*, phone: str, password: str, first_name: str, email: str) -> User:
    user = User(username=phone, first_name=first_name, email=email)
    user.set_password(raw_password=password)
    user.save()

    return user


def create_profile(*, user: User, profile_name: str, profile_type: str) -> Profile:
    profile = Profile(user=user, name=profile_name, type=profile_type)
    profile.save()

    return profile
