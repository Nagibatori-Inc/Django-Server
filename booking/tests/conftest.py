from booking.models import Advert
from review.tests.conftest import save_profile_object


def save_advert_object(advert: Advert) -> None:
    """Сохранить объект объявления, созданный фикстурой в бд"""
    if advert.promotion:
        advert.promotion.save()
    save_profile_object(advert.contact)
    advert.save()
