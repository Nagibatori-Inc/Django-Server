import pytest
from rest_framework import status
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.test import APIClient


pytestmark = pytest.mark.django_db


class TestAdverts:
    """Тесты на AdvertViewSet"""

    ADVERTS_LIST_URL = '/api/posts/'
    ADVERTS_RETRIEVE_URL = '/api/posts/{id}/'
    ADVERTS_CREATE_URL = '/api/posts/'
    ADVERTS_UPDATE_URL = '/api/posts/{id}/'
    ADVERTS_ACTIVATE_URL = '/api/posts/{id}/activate/'
    ADVERTS_DEACTIVATE_URL = '/api/posts/{id}/deactivate/'

    def test_unauthorized_request(self, api_client: APIClient):
        """
        Arrange: Неавторизованный клиент
        Act: Запрос к методам AdvertViewSet
        Assert: 401 ошибка
        """
        list_response = api_client.get(self.ADVERTS_LIST_URL)
        assert list_response.status_code == status.HTTP_401_UNAUTHORIZED

        retrieve_response = api_client.get(self.ADVERTS_RETRIEVE_URL.format(id=1))
        assert retrieve_response.status_code == status.HTTP_401_UNAUTHORIZED

        create_response = api_client.post(self.ADVERTS_CREATE_URL)
        assert create_response.status_code == status.HTTP_401_UNAUTHORIZED

        update_response = api_client.put(self.ADVERTS_UPDATE_URL.format(id=1))
        assert update_response.status_code == status.HTTP_401_UNAUTHORIZED

        activate_response = api_client.patch(self.ADVERTS_ACTIVATE_URL.format(id=1))
        assert activate_response.status_code == HTTP_401_UNAUTHORIZED

        deactivate_response = api_client.patch(self.ADVERTS_ACTIVATE_URL.format(id=1))
        assert deactivate_response.status_code == HTTP_401_UNAUTHORIZED
