import json

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient
from authentication.models import Profile

pytestmark = pytest.mark.django_db


class TestSignupView:
    def test_signup_user(self, api_client):
        pass


class TestProfileViewSet:
    basename = "profile-detail"

    def test_retrieve(self, api_client: APIClient, default_profile: Profile):
        expected_json = {"profile": {"name": default_profile.name, "type": default_profile.type}}

        # Получаем профиль
        url = reverse(self.basename, kwargs={"pk": default_profile.id})  # ignore: type[attr-defined]
        response = api_client.get(url)

        assert response.status_code == 200
        assert json.loads(response.content) == expected_json

    @pytest.mark.parametrize("logged_in_user, status_code", [("owner", 200), ("non-owner", 403), ("none", 403)])
    def test_update(self, api_client: APIClient, default_profile: Profile, logged_in_user: str, status_code: int):

        auth_user = {
            "owner": default_profile.user,
            "non-owner": baker.prepare(Profile, user__username="79188478732").user,
        }

        updated_data = {"profile": {"name": "HolyMoly", "type": default_profile.type}}

        if logged_in_user != "none":
            api_client.force_authenticate(user=auth_user[logged_in_user])

        url = reverse(self.basename, kwargs={"pk": default_profile.id})  # ignore: type[attr-defined]
        response = api_client.put(url, data=updated_data["profile"], format="json")

        assert response.status_code == status_code
        if logged_in_user == "owner":
            assert json.loads(response.content) == updated_data

    @pytest.mark.parametrize("logged_in_user, status_code", [("owner", 204), ("non-owner", 403), ("none", 403)])
    def test_destroy(self, api_client: APIClient, default_profile: Profile, logged_in_user: str, status_code: int):

        auth_user = {
            "owner": default_profile.user,
            "non-owner": baker.prepare(Profile, user__username="79188478732").user,
        }

        if logged_in_user != "none":
            api_client.force_authenticate(user=auth_user[logged_in_user])

        url = reverse(self.basename, kwargs={"pk": default_profile.id})  # ignore: type[attr-defined]

        # Удаляем профиль
        response = api_client.delete(url)
        assert response.status_code == status_code
