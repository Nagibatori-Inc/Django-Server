import string

import factory
from factory import fuzzy, SubFactory

from authentication.tests.factories import ProfileFactory
from booking.models import Advert, Promotion


class PromotionFactory(factory.Factory):
    """Фабрика модели Promotion"""

    type = fuzzy.FuzzyText()
    description = fuzzy.FuzzyText()

    class Meta:
        model = Promotion


class AdvertFactory(factory.Factory):
    """Фабрика модели Advert"""

    title = fuzzy.FuzzyText()
    description = fuzzy.FuzzyText()
    price = fuzzy.FuzzyDecimal(0, 1000000)
    contact = SubFactory(ProfileFactory)
    phone = fuzzy.FuzzyText(prefix='7', length=10, chars=string.digits)
    location = fuzzy.FuzzyText()
    views = fuzzy.FuzzyInteger(0, 10000)

    class Meta:
        model = Advert
