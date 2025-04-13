from typing import Tuple, Optional

from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db import transaction
from knox.models import AuthToken
from rest_framework.exceptions import ValidationError

from authentication.models import Profile
from authentication.utils import make_phone_uniform


class PasswordManagerService:
    def __init__(self, user: User):
        self.user = user

    def _check_if_password_same(self, new_password: str) -> None:
        old_password_hash = self.user.password
        if check_password(new_password, old_password_hash):
            raise ValidationError(detail={"detail": "new password is the same as the old one"})

    def reset_password(self, new_password: str) -> None:
        self._check_if_password_same(new_password)
        self.user.set_password(new_password)

        self.user.save(update_fields=["password"])


class ProfileManagerService:
    def __init__(self, profile: Profile):
        self.profile = profile

    @staticmethod
    def _update_user(*, user: User, **update_data) -> None:
        for name in update_data:
            new_val = update_data[name]

            if new_val is None:
                del update_data[name]
                continue

            if name == "password":
                user.set_password(raw_password=new_val)
                continue

            setattr(user, name, new_val)

        fields_to_update = list(update_data.keys())
        user.save(update_fields=fields_to_update)

    @staticmethod
    def _update_profile(*, profile: Profile, **update_data) -> None:
        for name in update_data:
            new_val = update_data[name]

            if new_val is None:
                del update_data[name]
                continue

            setattr(profile, name, new_val)

        fields_to_update = list(update_data.keys())
        profile.save(update_fields=fields_to_update)

    @staticmethod
    @transaction.atomic
    def create(
        phone: str, password: str, first_name: str, email: str, profile_name: str, profile_type: str
    ) -> Tuple[str, Profile]:
        phone = make_phone_uniform(phone)

        # Так как делается soft-delete, для сохранения пользовательских данных (ресурс очень нужный всем и везде),
        # нужно это учитывать, если пользователь "удалил" аккаунт, а потом решил создать новый, мы просто
        # обновляем его устаревшие данные и активируем аккаунт снова
        try:
            user = User.objects.select_related("profile").get(username=phone)
            profile = user.profile  # type: ignore[attr-defined]
            # Смотрим чтобы не обновили аккаунт активного пользователя
            if user.is_active:
                raise ValidationError(detail={"detail": "user with that phone already exists"})

            ProfileManagerService._update_user(
                user=user, password=password, first_name=first_name, email=email, is_active=True
            )
            ProfileManagerService._update_profile(
                profile=profile, name=profile_name, type=profile_type, is_deleted=False
            )

        except User.DoesNotExist:
            user = User(username=phone, first_name=first_name, email=email)
            profile = Profile(user=user, name=profile_name, type=profile_type)
            user.set_password(raw_password=password)

            user.save()
            profile.save()

        auth_token = AuthToken.objects.create(user)
        auth_token_val = auth_token[1]

        return auth_token_val, profile

    @transaction.atomic
    def update(
        self,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        name: Optional[str] = None,
        type: Optional[str] = None,
    ) -> None:
        ProfileManagerService._update_profile(profile=self.profile, name=name, type=type, is_deleted=False)
        ProfileManagerService._update_user(user=self.profile.user, username=phone, first_name=first_name, email=email)

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
