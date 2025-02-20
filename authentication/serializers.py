from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password as django_password_validate
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers, status

from DjangoServer.validators.password_validators import PhoneNumberValidator
from DjangoServer.validators.phone_number_re import RUS
from authentication.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", "type"]
        depth = 1


class SignUpRequestSerializer(serializers.Serializer):
    # Аттрибуты для юзера
    phone = serializers.CharField(required=True, max_length=15)
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, allow_blank=True)
    password = serializers.CharField(required=True)
    # Аттрибуты для профиля
    profile_name = serializers.CharField(required=False, max_length=50, allow_null=True)
    type = serializers.ChoiceField(choices=Profile.PROFILE_TYPE_CHOICES, default="IND")

    def validate_phone(self, value):
        phone_validator = PhoneNumberValidator(RUS)
        if not phone_validator(value):
            raise serializers.ValidationError(
                detail={"err_msg": "phone number invalid"},
                code="phone invalid")

        phone_used = (get_user_model()
                      .objects
                      .filter(username__exact=self.__make_phone_uniform(value)).exists())
        if phone_used:
            raise serializers.ValidationError(
                detail={"err_msg": "phone number already in use"},
                code="phone is used"
            )

        return value

    def validate_password(self, value):
        try:
            django_password_validate(value)
        except ValidationError as ex:
            raise serializers.ValidationError(
                detail={"err_msg": "password didn't pass validation", "err": ex},
                code="password invalid")
        return value

    # Сущность аутентификации не должна создаваться без профиля и наоборот 
    @transaction.atomic
    def create(self, validated_data):
        phone = validated_data.get("phone", None)
        password = validated_data.get("password", None)
        first_name = validated_data.get("first_name", None)

        email = validated_data.get("email", None)

        profile_name = validated_data.get("profile_name", None)
        type = validated_data.get("type", None)

        user = get_user_model().objects.create(username=phone, first_name=first_name, email=email, password=password)
        profile = Profile.objects.create(user=user, name=profile_name, type=type)
        return profile

    def __make_phone_uniform(self, phone: str):
        if phone.startswith("+7"):
            return "8" + phone[2:]
        elif phone.startswith("7"):
            return "8" + phone[1:]
        elif phone.startswith("+8"):
            return phone[1:]
        return phone
