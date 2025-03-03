from rest_framework import serializers

from authentication.models import Profile
from authentication.misc.validators import validate_password, validate_ru_phone, validate_otp

# Сделать два сериализатора для гет и для регистрации\данных своего профиля
class ProfileSerializer(serializers.ModelSerializer):
    # Добавить вложенного юзера
    class Meta:
        model = Profile
        fields = ["name", "type"]


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)

    def validate_password(self, value):
        validate_password(value)
        return value


class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, max_length=15)

    def validate_phone(self, value):
        validate_ru_phone(value)
        return value


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class VerificationRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, max_length=15)
    otp_code = serializers.CharField(required=True, max_length=6)

    def validate_phone(self, value):
        validate_ru_phone(value)
        return value

    def validate_otp_code(self, value):
        validate_otp(value)
        return value


class SignUpRequestSerializer(serializers.Serializer):
    # Аттрибуты для юзера
    phone = serializers.CharField(required=True, max_length=15)
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, allow_blank=True)
    password = serializers.CharField(required=True)
    # Аттрибуты для профиля
    profile_name = serializers.CharField(required=False, max_length=50, allow_null=True)
    profile_type = serializers.ChoiceField(choices=Profile.PROFILE_TYPE_CHOICES, default="IND")

    def validate_phone(self, value: str) -> str:
        validate_ru_phone(value)
        return value

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value



