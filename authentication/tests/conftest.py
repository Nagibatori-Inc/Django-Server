import pytest

from rest_framework.test import APIClient
from model_bakery import baker

from authentication.models import Profile


@pytest.fixture(scope="function")
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture(scope="session")
def mock_views_permissions():
    pass


@pytest.fixture(scope="function")
def default_profile() -> Profile:
    return baker.make_recipe("authentication.tests.profile_daniil")
