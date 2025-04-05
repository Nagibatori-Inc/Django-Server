from django.contrib.auth.models import User
from rest_framework import serializers

from authentication.models import Profile
from authentication.misc.validators import validate_password, validate_phone, validate_otp, PhoneValidationExp


class PhoneValidationMixin:

    def validate_phone(self, value: str) -> str:
        validate_phone(value, [PhoneValidationExp.RUS, PhoneValidationExp.BEL])
        return value


class PasswordValidationMixin:

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value


class OTPValidationMixin:

    def validate_otp_code(self, value: str) -> str:
        validate_otp(value)
        return value


class PhoneSerializer(serializers.Serializer, PhoneValidationMixin):
    phone = serializers.CharField(required=True, max_length=15)


class PasswordResetSerializer(serializers.Serializer, PasswordValidationMixin, OTPValidationMixin):
    password = serializers.CharField(required=True)
    otp_code = serializers.CharField(required=True, max_length=6)


class VerificationRequestSerializer(serializers.Serializer, PhoneValidationMixin, OTPValidationMixin):
    phone = serializers.CharField(required=True, max_length=15)
    otp_code = serializers.CharField(required=True, max_length=6)


class SignUpRequestSerializer(serializers.Serializer, PhoneValidationMixin, PasswordValidationMixin):
    # Аттрибуты для юзера
    phone = serializers.CharField(required=True, max_length=15)
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True, allow_blank=True)
    password = serializers.CharField(required=True)
    # Аттрибуты для профиля
    profile_name = serializers.CharField(required=False, max_length=50, allow_null=True)
    profile_type = serializers.ChoiceField(required=False, choices=Profile.PROFILE_TYPE_CHOICES, default="IND")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name"]


class ProfileOwnerSerializer(serializers.ModelSerializer):
    """Сериализатор, использующийся при удачном создании пользователя и при запросе данных о самом себе"""
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ["name", "type", "user"]


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор, используемый для получения данных о профиле иного (не себя) пользователя"""
    # Добавить вложенного юзера
    class Meta:
        model = Profile
        fields = ["name", "type"]
