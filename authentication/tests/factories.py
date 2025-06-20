import string

import factory
from django.contrib.auth.models import User
from factory import fuzzy

from authentication.models import Profile


class UserFactory(factory.Factory):
    """Фабрика модели User"""

    username = fuzzy.FuzzyText(prefix='7', length=10, chars=string.digits)
    first_name = fuzzy.FuzzyText()
    last_name = fuzzy.FuzzyText()

    class Meta:
        model = User


class ProfileFactory(factory.Factory):
    """Фабрика модели Profile"""

    name = fuzzy.FuzzyText()
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Profile
