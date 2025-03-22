from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password as django_password_validate
from django.core.exceptions import ValidationError
from rest_framework import serializers

from DjangoServer.validators.misc_validators import PhoneNumberValidator
from DjangoServer.validators.phone_regex import RUS
from authentication.models import Profile
from authentication.utils import make_phone_uniform


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", "type"]


class VerificationRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, max_length=15)
    otp_code = serializers.CharField(required=True, max_length=6)

    def validate(self, data):
        phone = data.get("phone", None)
        otp = data.get("otp_code", None)

        if len(otp) != 6:
            raise serializers.ValidationError(
                detail={"err_msg": "invalid otp length"}
            )

        phone_validator = PhoneNumberValidator(RUS)
        if not phone_validator(phone):
            raise serializers.ValidationError(
                detail={"err_msg": "phone number invalid"},
                code="phone invalid")

        phone = make_phone_uniform(phone)

        try:
            user = get_user_model().objects.get(username=phone)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError(
                detail={"err_msg": "no user with this phone"}
            )

        # could move these verifications to service
        if user.profile.is_verified:
            raise serializers.ValidationError(
                detail={"err_msg": "user already verified"}
            )

        return data


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



