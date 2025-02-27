from django.contrib.auth.models import User
from rest_framework import permissions


class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    """ Разрешение позволяющее менять профиль пользователя только самому пользователю """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user: User = request.user

        is_user_profile = user.profile == obj
        user_authenticated = user.is_authenticated

        return user_authenticated and is_user_profile
