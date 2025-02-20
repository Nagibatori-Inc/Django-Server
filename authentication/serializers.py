from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password as django_password_validate
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers, status


from authentication.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["id", "name", "type"]
        depth = 1


class SignUpRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(required=True)

    profile_name = serializers.CharField(max_length=50, allow_null=True)
    type = serializers.ChoiceField(choices=Profile.PROFILE_TYPE_CHOICES, default="IND")

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
        first_name = validated_data.get("first_name", None)
        email = validated_data.get("email", None)
        password = validated_data.get("password", None)
        profile_name = validated_data.get("profile_name", None)
        type = validated_data.get("type", None)

        user = get_user_model().objects.create(username=phone, first_name=first_name, email=email, password=password)
        profile = Profile.objects.create(user=user, name=profile_name, type=type)
        return profile
