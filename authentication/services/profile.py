from typing import Tuple

from django.db import transaction, IntegrityError
from django.contrib.auth.hashers import check_password
from knox.models import User, AuthToken
from rest_framework.exceptions import ValidationError

from authentication.models import Profile
from authentication.utils import make_phone_uniform


class PasswordManagerService:
    def __init__(self, user: User):
        self.user = user

    def _check_if_password_same(self, new_password):
        old_password = self.user.password
        if check_password(new_password, old_password):
            raise ValidationError(
                detail={"detail": "new password is the same as the old one"}
            )

    def reset_password(self, new_password):
        self._check_if_password_same(new_password)
        self.user.set_password(new_password)

        self.user.save(update_fields=["password"])


class ProfileManagerService:
    def __init__(self, profile):
        self.profile = profile

    @staticmethod
    @transaction.atomic
    def create(phone, password, first_name, email, profile_name, profile_type) -> Tuple[AuthToken, Profile]:
        phone = make_phone_uniform(phone)
        user = User(username=phone, first_name=first_name, email=email)
        user.set_password(raw_password=password)

        try:
            user.save()
        except IntegrityError:
            raise ValidationError(detail={"detail": "user with that phone already exists"})

        auth_token = AuthToken.objects.create(user)
        profile = Profile(user=user, name=profile_name, type=profile_type)
        profile.save()

        return auth_token, profile

    def update(self, name: str, type: str):
        self.profile.name = name
        self.profile.type = type

        self.profile.save(update_fields=["name", "type"])

    def verify(self):
        self.profile.is_verified = True

        self.profile.save(update_fields=["is_verified"])

    @transaction.atomic
    def soft_delete(self) -> None:
        related_user = self.profile.user

        self.profile.is_deleted = True
        related_user.is_active = False

        self.profile.save(update_fields=["is_deleted"])
        related_user.save(update_fields=["is_active"])
