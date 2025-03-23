from rest_framework import permissions


class IsProfileOwnerOrReadOnly(permissions.BasePermission):  # type: ignore[misc]
    """ Разрешение позволяющее менять профиль пользователя только самому пользователю """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return not request.user.is_anonymous and request.user.profile == obj
