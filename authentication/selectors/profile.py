from django.shortcuts import get_object_or_404


from authentication.models import Profile


def get_profile_by_id(profile_id: int) -> Profile:
    """
    Получить профиль по id
    :param profile_id: id профиля
    :return: Объект Profile с id=profile_id
    """
    return get_object_or_404(Profile, id=profile_id)
