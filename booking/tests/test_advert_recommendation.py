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
        Arrange:
        Act:
        Assert:
        """
        for advert in adverts:
            save_advert_object(advert)

        response = api_client.get(self.ADVERT_RECOMMENDATION_LIST_URL)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.data if response.data else []  # type: ignore[arg-type]
        assert len(response_data) == count_return_adverts
        for advert in response_data:
            assert advert['status'] == AdvertStatus.ACTIVE  # type: ignore[index]
