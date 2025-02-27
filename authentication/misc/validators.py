import re

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password as django_password_validate
from django.core.exceptions import ValidationError as DjangoValidationError

RUS = r"^(\+7|8|7|\+8)\d{10}"


class PhoneNumberValidator:
    def __init__(self, re_exp):
        self.re_exp = re_exp

    def __call__(self, phone):
        phone_valid = re.match(self.re_exp, phone)
        return phone_valid is not None


def validate_ru_phone(phone: str) -> None:
    phone_validator = PhoneNumberValidator(RUS)
    if not phone_validator(phone):
        raise serializers.ValidationError(
            detail={"detail": "phone number valid"}
        )


def validate_password(password: str) -> None:
    try:
        django_password_validate(password)
    except DjangoValidationError as ex:
        raise serializers.ValidationError(
            detail={"detail": "password didn't pass validation", "err": ex}
        )


def validate_otp(otp: str) -> None:
    if len(otp) != 6:
        raise serializers.ValidationError(
            detail={"detail": "invalid otp length"}
        )
