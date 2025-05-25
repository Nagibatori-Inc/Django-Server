from typing import Any

import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.test import APIClient

from authentication.models import Profile
from booking.models import Advert, AdvertStatus
from booking.tests.factories import AdvertFactory

from booking.tests.conftest import save_advert_object


pytestmark = pytest.mark.django_db


class TestAdverts:
    """Тесты на AdvertViewSet"""

    ADVERTS_LIST_URL = '/api/posts/'
    ADVERTS_RETRIEVE_URL = '/api/posts/{id}/'
    ADVERTS_CREATE_URL = '/api/posts/'
    ADVERTS_UPDATE_URL = '/api/posts/{id}/'
    ADVERTS_ACTIVATE_URL = '/api/posts/{id}/activate/'
    ADVERTS_DEACTIVATE_URL = '/api/posts/{id}/deactivate/'

    SUCCESS_ADVERT_UPDATE_REQUEST_DATA = {
        "title": "Новое название",
        "description": "Новое описание",
        "price": "1000.00",
        "phone": "79999999999",
        "location": "Новая локация",
        "views": 123123,
        "activated_at": "2025-05-14T20:36:39.573115Z",
        "status": "ACTIVE",
        "active_until": "2025-05-17T18:54:54Z",
    }

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

    @pytest.mark.parametrize(
        'adverts, count_returned_adverts',
        (
            (
                [
                    AdvertFactory(status=AdvertStatus.ACTIVE),
                    AdvertFactory(status=AdvertStatus.ACTIVE),
                    AdvertFactory(status=AdvertStatus.ACTIVE),
                ],
                3,
            ),
            (
                [],
                0,
            ),
        ),
    )
    def test_success_list_request(
        self, auth_client: APIClient, auth_profile: Profile, adverts: list[Advert], count_returned_adverts: int
    ):
        """
        Arrange: Авторизованный профиль.
                 1. 3 объявления профиля
                 2. 0 объявлений профиля
        Act: Запрос на получение объявлений профиля
        Assert: Код ответа 200, вернулось корректное количество объектов
        """
        for advert in adverts:
            advert.contact = auth_profile
            save_advert_object(advert)

        response = auth_client.get(self.ADVERTS_LIST_URL)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data if response.data else []) == count_returned_adverts  # type: ignore[arg-type]

    def test_profile_not_found_list_request(self, api_client: APIClient, auth_user: User):
        """
        Arrange: Авторизованный клиент, в бд есть только объект User
        Act: Запрос на получение объявлений
        Assert: 404 ошибка
        """
        auth_user.save()
        api_client.force_authenticate(user=auth_user)

        response = api_client.get(self.ADVERTS_LIST_URL)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_success_retrieve_advert_request(self, auth_client: APIClient, auth_profile_advert: Advert):
        """
        Arrange: Авторизованный клиент, в бд есть сохраненный объект объявления от авторизованного профиля
        Act: Запрос на получение объявления
        Assert: Код ответа 200, вернулось корректное объявления
        """
        save_advert_object(auth_profile_advert)

        response = auth_client.get(self.ADVERTS_RETRIEVE_URL.format(id=auth_profile_advert.pk))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == auth_profile_advert.pk

    def test_profile_not_found_retrieve_request(self, api_client: APIClient, auth_user: User):
        """
        Arrange: Авторизованный клиент, в бд есть только объект User
        Act: Запрос на получение объявления
        Assert: 404 ошибка
        """
        auth_user.save()
        api_client.force_authenticate(user=auth_user)
        fake_advert_id = 1

        response = api_client.get(self.ADVERTS_RETRIEVE_URL.format(id=fake_advert_id))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_advert_not_found_retrieve_request(self, auth_client: APIClient, auth_profile_advert: Advert):
        """
        Arrange: Авторизованный клиент, в бд есть объект объявления от авторизованного профиля
        Act: Запрос на получение объявления с неправильным id
        Assert: 404 ошибка
        """
        save_advert_object(auth_profile_advert)
        wrong_advert_id = auth_profile_advert.pk + 1

        response = auth_client.get(self.ADVERTS_RETRIEVE_URL.format(id=wrong_advert_id))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        'request_data, status_code',
        (
            (
                {
                    'title': 'CorrectTitle',
                    'description': 'CorrectDescription',
                    'price': 1123,
                    'phone': '123123123',
                    'location': 'CorrectLocation',
                    'status': AdvertStatus.DISABLED,
                },
                status.HTTP_201_CREATED,
            ),
            ({}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ),
    )
    def test_advert_creation_request(self, auth_client: APIClient, request_data: dict[str, Any], status_code: int):
        """
        Arrange: Авторизованный клиент, данные для создания объявления
        Act: Запрос на создание объявления
        Assert: 1. Код ответа 200, в бд создалось новое объявление с корректными данными
                2. 422 ошибка
        """
        response = auth_client.post(self.ADVERTS_CREATE_URL, data=request_data)

        assert response.status_code == status_code
        if response.status_code == status.HTTP_201_CREATED:
            assert Advert.objects.filter(**request_data).exists()

    def test_profile_not_found_update_request(
        self, api_client: APIClient, auth_user: User, auth_profile_advert: Advert
    ):
        """
        Arrange: Авторизованный клиент, в бд есть только объект User
        Act: Запрос на изменение объявления
        Assert: 404 ошибка
        """
        auth_user.save()
        api_client.force_authenticate(user=auth_user)
        fake_advert_id = 1

        response = api_client.put(self.ADVERTS_UPDATE_URL.format(id=fake_advert_id))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_advert_not_found_update_request(self, auth_client: APIClient, auth_profile_advert: Advert):
        """
        Arrange: Авторизованный клиент, в бд есть объект объявления от авторизованного профиля
        Act: Запрос на изменение объявления с неправильным id
        Assert: 404 ошибка
        """
        save_advert_object(auth_profile_advert)
        wrong_advert_id = auth_profile_advert.pk + 1

        request_data = self.SUCCESS_ADVERT_UPDATE_REQUEST_DATA
        request_data['contact'] = auth_profile_advert.contact.pk

        response = auth_client.put(self.ADVERTS_RETRIEVE_URL.format(id=wrong_advert_id), data=request_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        'request_data', SUCCESS_ADVERT_UPDATE_REQUEST_DATA
    )  # Сюда потом можно больше кейсов добавить
    def test_advert_update_request(
        self, auth_client: APIClient, auth_profile_advert: Advert, request_data: dict[str, Any]
    ):
        """
        Arrange: Авторизованный клиент, данные для обновления объявления
        Act: Запрос на создание объявления
        Assert: Код ответа 200, данные объявления изменились
        """
        save_advert_object(auth_profile_advert)
        request_data = self.SUCCESS_ADVERT_UPDATE_REQUEST_DATA
        request_data['contact'] = auth_profile_advert.contact.pk

        response = auth_client.put(self.ADVERTS_UPDATE_URL.format(id=auth_profile_advert.pk), data=request_data)

        assert response.status_code == status.HTTP_200_OK
        assert Advert.objects.filter(pk=auth_profile_advert.pk, **request_data).exists()

    def test_profile_not_found_activate_request(
        self, api_client: APIClient, auth_user: User, auth_profile_advert: Advert
    ):
        """
        Arrange: Авторизованный клиент, в бд есть только объект User
        Act: Запрос на активацию объявления
        Assert: 404 ошибка
        """
        auth_user.save()
        api_client.force_authenticate(user=auth_user)
        fake_advert_id = 1

        response = api_client.patch(self.ADVERTS_ACTIVATE_URL.format(id=fake_advert_id))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_advert_not_found_activate_request(self, auth_client: APIClient, auth_profile_advert: Advert):
        """
        Arrange: Авторизованный клиент, в бд есть объект объявления от авторизованного профиля
        Act: Запрос на активацию объявления с неправильным id
        Assert: 404 ошибка
        """
        save_advert_object(auth_profile_advert)
        wrong_advert_id = auth_profile_advert.pk + 1

        response = auth_client.patch(self.ADVERTS_ACTIVATE_URL.format(id=wrong_advert_id))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('advert_status', (AdvertStatus.DRAFT, AdvertStatus.DRAFT))
    def test_advert_activate_request(
        self,
        auth_client: APIClient,
        auth_profile_advert: Advert,
        advert_status: AdvertStatus,
    ):
        """
        Arrange: Авторизованный клиент, объект объявления в бд
        Act: Запрос на активацию объявления
        Assert: Код ответа 200, данные объявления изменились
        """
        auth_profile_advert.status = advert_status
        save_advert_object(auth_profile_advert)

        response = auth_client.patch(self.ADVERTS_ACTIVATE_URL.format(id=auth_profile_advert.pk))

        assert response.status_code == status.HTTP_200_OK
        assert Advert.objects.get(pk=auth_profile_advert.pk).is_active

    def test_profile_not_found_deactivate_request(
        self, api_client: APIClient, auth_user: User, auth_profile_advert: Advert
    ):
        """
        Arrange: Авторизованный клиент, в бд есть только объект User
        Act: Запрос на деактивацию объявления
        Assert: 404 ошибка
        """
        auth_user.save()
        api_client.force_authenticate(user=auth_user)
        fake_advert_id = 1

        response = api_client.patch(self.ADVERTS_DEACTIVATE_URL.format(id=fake_advert_id))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_advert_not_found_deactivate_request(self, auth_client: APIClient, auth_profile_advert: Advert):
        """
        Arrange: Авторизованный клиент, в бд есть объект объявления от авторизованного профиля
        Act: Запрос на деактивацию объявления с неправильным id
        Assert: 404 ошибка
        """
        save_advert_object(auth_profile_advert)
        wrong_advert_id = auth_profile_advert.pk + 1

        response = auth_client.patch(self.ADVERTS_DEACTIVATE_URL.format(id=wrong_advert_id))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_advert_deactivate_request(self, auth_client: APIClient, auth_profile_advert: Advert):
        """
        Arrange: Авторизованный клиент, объект объявления в бд
        Act: Запрос на деактивацию объявления
        Assert: Код ответа 200, данные объявления изменились
        """
        auth_profile_advert.status = AdvertStatus.ACTIVE
        save_advert_object(auth_profile_advert)

        response = auth_client.patch(self.ADVERTS_DEACTIVATE_URL.format(id=auth_profile_advert.pk))

        assert response.status_code == status.HTTP_200_OK
        assert not Advert.objects.get(pk=auth_profile_advert.pk).is_active
