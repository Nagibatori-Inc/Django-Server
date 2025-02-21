from typing import Dict, Tuple

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password as django_password_validate
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers, status

from DjangoServer.validators.misc_validators import PhoneNumberValidator
from DjangoServer.validators.phone_number_re import RUS
from authentication.models import Profile, OneTimePassword
from authentication.utils import make_phone_uniform


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", "type"]


class SignUpRequestSerializer(serializers.Serializer):
    # Аттрибуты для юзера
    phone = serializers.CharField(required=True, max_length=15)
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, allow_blank=True)
    password = serializers.CharField(required=True)
    # Аттрибуты для профиля
    profile_name = serializers.CharField(required=False, max_length=50, allow_null=True)
    type = serializers.ChoiceField(choices=Profile.PROFILE_TYPE_CHOICES, default="IND")

    def validate_phone(self, value: str) -> str:
        phone_validator = PhoneNumberValidator(RUS)
        if not phone_validator(value):
            raise serializers.ValidationError(
                detail={"err_msg": "phone number invalid"},
                code="phone invalid")

        phone_used = (get_user_model()
                      .objects
                      .filter(username__exact=make_phone_uniform(value)).exists())
        if phone_used:
            raise serializers.ValidationError(
                detail={"err_msg": "phone number already in use"},
                code="phone is used"
            )

        return value

    def validate_password(self, value: str) -> str:
        try:
            django_password_validate(value)
        except ValidationError as ex:
            raise serializers.ValidationError(
                detail={"err_msg": "password didn't pass validation", "err": ex},
                code="password invalid")
        return value

    # Сущность аутентификации не должна создаваться без профиля и наоборот 
    @transaction.atomic
    def create(self, validated_data: Dict[str, str]) -> Tuple[Profile, str]:
        phone = validated_data.get("phone", None)
        password = validated_data.get("password", None)
        first_name = validated_data.get("first_name", None)

        email = validated_data.get("email", None)

        profile_name = validated_data.get("profile_name", None)
        type = validated_data.get("type", None)

        phone = make_phone_uniform(phone)

        user_model = get_user_model()
        user = user_model(username=phone, first_name=first_name, email=email)
        user.set_password(raw_password=password)
        user.save()

        otp = OneTimePassword(user=user)
        otp = otp.save()

        profile = Profile.objects.create(user=user, name=profile_name, type=type)
        return profile, otp


