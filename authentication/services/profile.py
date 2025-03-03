from typing import Tuple

from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from knox.models import AuthToken
from rest_framework.exceptions import ValidationError

from authentication.models import Profile
from authentication.utils import make_phone_uniform, update_user, update_profile, create_user, create_profile


class PasswordManagerService:
    def __init__(self, user: User):
        self.user = user

    def _check_if_password_same(self, new_password: str) -> None:
        old_password_hash = self.user.password
        if check_password(new_password, old_password_hash):
            raise ValidationError(
                detail={"detail": "new password is the same as the old one"}
            )

    def reset_password(self, new_password: str) -> None:
        self._check_if_password_same(new_password)
        self.user.set_password(new_password)

        self.user.save(update_fields=["password"])


class ProfileManagerService:
    def __init__(self, profile: Profile):
        self.profile = profile

    @staticmethod
    @transaction.atomic
    def create(phone: str, password: str, first_name: str, email: str, profile_name: str, profile_type: str) -> Tuple[str, Profile]:
        user: User
        profile: Profile

        phone = make_phone_uniform(phone)

        # Так как делается soft-delete, для сохранения пользовательских данных (ресурс очень нужный всем и везде),
        # нужно это учитывать, если пользователь "удалил" аккаунт, а потом решил создать новый, мы просто
        # обновляем его устаревшие данные и активируем аккаунт снова
        try:
            user = User.objects.select_related("profile").get(username=phone)
            profile = user.profile
            # Смотрим чтобы не обновили аккаунт активного пользователя
            if user.is_active:
                raise ValidationError(detail={"detail": "user with that phone already exists"})

            update_user(user=user, password=password, first_name=first_name, email=email, is_active=True)
            update_profile(profile=profile, profile_name=profile_name, profile_type=profile_type, is_deleted=False)

        except User.DoesNotExist:
            user = create_user(phone=phone, password=password, first_name=first_name, email=email)
            profile = create_profile(user=user, profile_type=profile_type, profile_name=profile_name)

        auth_token = AuthToken.objects.create(user)
        auth_token_val = auth_token[1]

        return auth_token_val, profile

    def update(self, name: str, type: str) -> None:
        self.profile.name = name
        self.profile.type = type

        self.profile.save(update_fields=["name", "type"])

    def verify(self) -> None:
        if self.profile.is_verified:
            raise ValidationError(detail={"detail": "user already verified"})

        self.profile.is_verified = True
        self.profile.save(update_fields=["is_verified"])

    @transaction.atomic
    def soft_delete(self) -> None:
        related_user: User = self.profile.user

        self.profile.is_deleted = True
        related_user.is_active = False

        self.profile.save(update_fields=["is_deleted"])
        related_user.save(update_fields=["is_active"])
