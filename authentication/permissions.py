from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

from authentication.models import Profile


class IsProfileOwnerOrReadOnly(permissions.BasePermission):  # type: ignore[misc]
    """Разрешение позволяющее менять профиль пользователя только самому пользователю"""

    def has_object_permission(self, request, view, obj: Profile) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        is_profile_owner = obj.user == user

        return is_profile_owner


class HasModeratorPermissions(IsAuthenticated):  # type: ignore[misc]
    """Проверка что пользователь - модератор"""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.profile.type == Profile.ProfileType.MODERATOR
