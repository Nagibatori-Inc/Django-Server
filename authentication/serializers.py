from django.contrib.auth.models import User
from rest_framework import serializers

from authentication.models import Profile
from authentication.misc.validators import validate_password, validate_phone, validate_otp, PhoneValidationExp

# Можно заметить, что поля повторяются и, в целом, для них можно сделать mixin'ы или type alias'ы,
# но сразу не будет видно какие аттрибуты обрабатываются этим сериализатором, что не очень хорошо
# для читаемости


class PhoneValidationMixin:
    """Mixin для валидации телефонного номера"""

    def validate_phone(self, value: str) -> str:
        validate_phone(value, [PhoneValidationExp.RUS, PhoneValidationExp.BEL])
        return value


class PasswordValidationMixin:
    """Mixin для валидации пароля"""

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value


class OTPValidationMixin:
    """Mixin для валидации OTP кода"""

    def validate_otp_code(self, value: str) -> str:
        validate_otp(value)
        return value


class PhoneSerializer(serializers.Serializer, PhoneValidationMixin):
    phone = serializers.CharField(required=True, max_length=15)


class PasswordResetSerializer(
    serializers.Serializer, PasswordValidationMixin, OTPValidationMixin, PhoneValidationMixin
):
    phone = serializers.CharField(required=True, max_length=15)
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
    profile_type = serializers.ChoiceField(required=False, choices=Profile.ProfileType.choices, default="IND")


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[])

    class Meta:
        model = User
        fields = ["username", "email", "first_name"]


class ProfileOwnerSerializer(serializers.ModelSerializer):
    """Сериализатор, использующийся при удачном создании пользователя и при запросе данных о самом себе"""

    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ["id", "name", "type", "user"]
        read_only_fields = ["id"]

    # Убираем вложенность при отправке клиенту
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        user_data = representation.pop("user")
        user_data["phone"] = user_data.pop("username")

        representation.update(user_data)
        return representation

    # Убираем вложенность при получении (нужно для дальнейшего разворачивания)
    def to_internal_value(self, data):
        new_data = super().to_internal_value(data)
        user_data = new_data.pop("user")
        user_data["phone"] = user_data.pop("username")

        new_data.update(user_data)
        return new_data


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор, используемый для получения данных о профиле иного (не себя) пользователя"""

    # Добавить вложенного юзера
    class Meta:
        model = Profile
        fields = ["name", "type"]
