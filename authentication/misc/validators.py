import re
from enum import Enum

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password as django_password_validate
from django.core.exceptions import ValidationError as DjangoValidationError


class PhoneValidationExp(str, Enum):
    RUS = r"^(\+7|8|7|\+8)\d{10}"
    BEL = r"^(\+10|9|10|\+9)\d{10}"  # Просто пример


class PhoneNumberValidator:
    def __init__(self, re_exps: list[PhoneValidationExp]) -> None:
        self.re_exps = re_exps

    def __call__(self, phone: str) -> bool:
        for re_exp in self.re_exps:
            phone_valid = re.match(re_exp, phone)
            if phone_valid is not None:
                return True
        return False


def validate_phone(phone: str, validation_templates: list[PhoneValidationExp]) -> None:
    phone_validator = PhoneNumberValidator(validation_templates)
    if not phone_validator(phone):
        raise serializers.ValidationError(detail={"detail": "phone number invalid"})


def validate_password(password: str) -> None:
    try:
        django_password_validate(password)
    except DjangoValidationError as ex:
        raise serializers.ValidationError(detail={"detail": f"password didn't pass validation {ex}"})


def validate_otp(otp: str) -> None:
    if len(otp) != 6:
        raise serializers.ValidationError(detail={"detail": "invalid otp length"})
