import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

from authentication.models import Profile
from authentication.tests.factories import UserFactory, ProfileFactory


LOGIN_URL_NAME = 'login'


@pytest.fixture
def api_client() -> APIClient:
    """Фикстура api клиента"""
    return APIClient()


@pytest.fixture
def auth_user() -> User:
    """Фикстура залогиненого пользователя"""
    return UserFactory()


@pytest.fixture
def auth_profile(auth_user: User) -> Profile:
    """Фикстура залогиненного профиля"""
    return ProfileFactory(user=auth_user)


@pytest.fixture
def auth_client(api_client: APIClient, auth_user: User, auth_profile: Profile) -> APIClient:
    """Фикстура залогиненного клиента"""
    auth_user.save()
    auth_profile.save()
    api_client.force_authenticate(user=auth_user)
    api_client.post(reverse(LOGIN_URL_NAME))
    return api_client


@pytest.fixture
def profile() -> Profile:
    """Фикстура профиля"""
    return ProfileFactory()
