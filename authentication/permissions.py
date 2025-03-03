from django.contrib.auth.models import User
from rest_framework import permissions

from authentication.models import Profile


class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    """ Разрешение позволяющее менять профиль пользователя только самому пользователю """

    def has_object_permission(self, request, view, obj: Profile) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        user: User = request.user
        if not user.is_authenticated:
            return False

        is_user_profile = user.profile == obj

        return is_user_profile
