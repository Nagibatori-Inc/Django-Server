import pytest

from authentication.models import Profile
from booking.models import Advert
from booking.tests.factories import AdvertFactory
from review.tests.conftest import save_profile_object


def save_advert_object(advert: Advert) -> None:
    """Сохранить объект объявления, созданный фикстурой в бд"""
    if advert.promotion:
        advert.promotion.save()
    save_profile_object(advert.contact)
    advert.save()


@pytest.fixture
def auth_profile_advert(auth_profile: Profile) -> Advert:
    """Фикстура объявления, оставленного профилем auth_profile"""
    return AdvertFactory(contact=auth_profile)


@pytest.fixture
def advert() -> Advert:
    """Фикстура объявления"""
    return AdvertFactory()
