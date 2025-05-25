import pytest
from rest_framework import status
from rest_framework.test import APIClient

from booking.models import Advert, AdvertStatus
from booking.tests.conftest import save_advert_object
from booking.tests.factories import AdvertFactory

pytestmark = pytest.mark.django_db


class TestAdvertRecommendation:

    ADVERT_RECOMMENDATION_LIST_URL = '/api/adverts/'
    ADVERT_RECOMMENDATION_RETRIEVE_URL = '/api/adverts/{id}/'
    ADVERT_RECOMMENDATION_FILTER_URL = '/api/adverts/filter/'

    @pytest.mark.parametrize(
        'adverts, count_return_adverts',
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
                [
                    AdvertFactory(status=AdvertStatus.ACTIVE),
                    AdvertFactory(status=AdvertStatus.DISABLED),
                    AdvertFactory(status=AdvertStatus.DRAFT),
                ],
                1,
            ),
            ([], 0),
        ),
    )
    def test_list_request(self, api_client: APIClient, adverts: list[Advert], count_return_adverts: int):
        """
        Arrange: Объявления в бд
        Act: Запрос на получение объявлений
        Assert: Вернулись корректные данные
        """
        for advert in adverts:
            save_advert_object(advert)

        response = api_client.get(self.ADVERT_RECOMMENDATION_LIST_URL)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.data if response.data else []  # type: ignore[arg-type]
        assert len(response_data) == count_return_adverts
        for advert in response_data:
            assert advert['status'] == AdvertStatus.ACTIVE  # type: ignore[index]

    def test_retrieve_request_with_active_advert(self, api_client: APIClient, advert: Advert):
        """
        Arrange: Активированное объявление в бд
        Act: Запрос на получение объявления по id
        Assert: Код ответа 200, вернулось корректное объявление
        """
        advert.status = AdvertStatus.ACTIVE
        save_advert_object(advert)

        response = api_client.get(self.ADVERT_RECOMMENDATION_RETRIEVE_URL.format(id=advert.pk))

        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]['id'] == advert.pk  # type: ignore[index]

    @pytest.mark.parametrize('advert_status', (AdvertStatus.DRAFT, AdvertStatus.DISABLED))
    def test_retrieve_request_with_not_active_advert(
        self, api_client: APIClient, advert: Advert, advert_status: AdvertStatus
    ):
        """
        Arrange: Не активированное объявление в бд
        Act: Запроса на получение объявления по id
        Assert: 404 ошибка
        """
        advert.status = advert_status
        save_advert_object(advert)

        response = api_client.get(self.ADVERT_RECOMMENDATION_RETRIEVE_URL.format(id=advert.pk))

        assert response.status_code == status.HTTP_404_NOT_FOUND
