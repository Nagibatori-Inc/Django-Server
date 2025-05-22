import factory
from factory import fuzzy

from authentication.tests.factories import ProfileFactory
from review.models import Review


class ReviewFactory(factory.Factory):
    """Фабрика модели Review"""

    rate = fuzzy.FuzzyInteger(low=1, high=5)
    text = fuzzy.FuzzyText()

    profile = factory.SubFactory(ProfileFactory)
    author = factory.SubFactory(ProfileFactory)

    class Meta:
        model = Review
