from rest_framework import permissions

from booking.models import Advert


class IsAdvertOwnerOrReadOnly(permissions.BasePermission):  # type: ignore[misc]
    def has_object_permission(self, request, view, obj: Advert) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        profile = request.user.profile
        is_advert_owner = obj.contact == profile

        return is_advert_owner
