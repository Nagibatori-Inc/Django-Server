import pytest
from rest_framework import serializers

from authentication.misc.validators import validate_phone, PhoneValidationExp

pytestmark = pytest.mark.unit


class TestPhoneValidation:

    @pytest.mark.parametrize(
        "phone",
        [
            "79811397566",
            "+79811397566",
            "+89811397566",
            "89811397566",
            "109811397566",
            "+109811397566",
            "+99811397566",
            "99811397566",
        ],
    )
    def test_valid_phone(self, phone: str):
        validate_phone(phone, [PhoneValidationExp.RUS, PhoneValidationExp.BEL])

    @pytest.mark.parametrize("phone", ["9811397566", "+9811397566", "+1324189811397566", "8569811397566"])
    def test_invalid_phone(self, phone: str):
        with pytest.raises(serializers.ValidationError):
            validate_phone(phone, [PhoneValidationExp.RUS, PhoneValidationExp.BEL])
