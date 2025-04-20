from rest_framework import permissions

from authentication.models import Profile


class IsProfileOwnerOrReadOnly(permissions.BasePermission):  # type: ignore[misc]
    """Разрешение позволяющее менять профиль пользователя только самому пользователю"""

    def has_object_permission(self, request, view, obj: Profile) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        is_profile_owner = obj.user == user

        return is_profile_owner
