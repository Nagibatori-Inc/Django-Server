import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from authentication.models import Profile
from review.models import Review
from review.tests.conftest import save_review_object, save_profile_object


pytestmark = pytest.mark.django_db


class TestModerateReviews:
    """Тесты на ModerateReviewAPIView"""

    moderate_review_url_name = 'moderate_review'

    def test_unauthorized_get_request(self, api_client: APIClient):
        """
        Arrange: Неавторизованный клиент
        Act: Запрос на получение страницы модерирования отзывов
        Assert: 401 ошибка
        """
        response = api_client.get(reverse(self.moderate_review_url_name))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_reviews_request_not_from_moderator(self, auth_client: APIClient, auth_profile: Profile):
        """
        Arrange: Авторизованный профиль не модератора
        Act: Запрос на получение страницы модерирования отзывов
        Assert: 403 ошибка
        """
        response = auth_client.get(reverse(self.moderate_review_url_name))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_success_get_reviews_request(self, auth_client: APIClient):
        """
        Arrange: Авторизованный профиль модератора
        Act: Запрос на получение страницы модерирования отзывов
        Assert: Код ответа 200
        """
        response = auth_client.get(reverse(self.moderate_review_url_name))

        assert response.status_code == status.HTTP_200_OK

    def test_unauthorized_moderate_review_request(self, api_client: APIClient):
        """
        Arrange: Неавторизованный клиент
        Act: Запрос на получение страницы модерирования отзывов
        Assert: 401 ошибка
        """
        response = api_client.post(reverse(self.moderate_review_url_name))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_moderate_review_request_not_from_moderator(self, auth_client: APIClient, auth_profile: Profile):
        """
        Arrange: Авторизованный профиль не модератора
        Act: Запрос на получение страницы модерирования отзывов
        Assert: 403 ошибка
        """
        response = auth_client.post(reverse(self.moderate_review_url_name))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        'is_approved, response_code',
        (
            (True, status.HTTP_200_OK),
            (False, status.HTTP_200_OK),
            ('invalid_data', status.HTTP_400_BAD_REQUEST),
        ),
    )
    def test_moderate_review_request_from_moderator(
        self,
        auth_client: APIClient,
        auth_profile: Profile,
        review: Review,
        is_approved: bool,
        response_code: int,
    ):
        """
        Arrange: Авторизованный профиль модератора, отзыв для модерации
        Act: Запрос на модерацию отзыва
        Assert: 1. Код ответа 200, в бд есть объект отзыва с корректными данными
                2. Код ответа 200, отзыв удален из бд
                3. 400 ошибка
        """
        save_review_object(review=review)
        auth_profile.type = Profile.ProfileType.MODERATOR
        save_profile_object(profile=auth_profile)
        request_data = {
            'review_id': review.pk,
            'is_approved': is_approved,
        }

        assert not Review.objects.get(pk=review.pk).is_approved

        response = auth_client.post(path=reverse(self.moderate_review_url_name), data=request_data)

        assert response.status_code == response_code
        if response_code == status.HTTP_200_OK:
            if is_approved:
                moderated_review = Review.objects.get(pk=review.pk)
                assert moderated_review.is_approved == is_approved
                assert moderated_review.approved_by == auth_profile
            else:
                assert not Review.objects.filter(pk=review.pk).exists()
