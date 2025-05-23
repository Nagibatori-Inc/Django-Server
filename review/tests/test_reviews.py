from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import Profile
from review.models import Review
from review.tests.factories import ReviewFactory


pytestmark = pytest.mark.django_db


SUCCESS_CREATE_REVIEW_REQUEST_BODY = {'text': 'Тестовый текст отзыва', 'rate': 4}


def _save_profile_object(profile: Profile) -> None:
    profile.user.save()
    profile.save()


def _save_review_object(review: Review) -> None:
    _save_profile_object(profile=review.profile)
    _save_profile_object(profile=review.author)
    review.save()


@pytest.fixture
def review_form_unauth_profile(profile: Profile) -> Review:
    return ReviewFactory(author=profile)


@pytest.fixture
def review_form_auth_profile(auth_profile: Profile) -> Review:
    return ReviewFactory(author=auth_profile)


class TestProfilesReview:
    """Тесты на вью ProfileReviewsAPIView"""

    profile_reviews_url_name = 'profile_reviews'

    @pytest.mark.parametrize(
        'reviews, count_returned_reviews',
        [
            ((ReviewFactory(is_approved=True), ReviewFactory(is_approved=True)), 2),
            ((ReviewFactory(is_approved=False), ReviewFactory(is_approved=True)), 1),
            (tuple(), 0),
        ],
    )
    def test_get_reviews_success_request(
        self,
        profile: Profile,
        reviews: tuple[Review],
        count_returned_reviews: int,
        api_client: APIClient,
    ):
        """
        Arrange: Объекты отзывов в бд
        Act: Запрос на получение отзывов профиля
        Assert: Количество возвращаемых объектов совпадает
        """
        _save_profile_object(profile=profile)
        for review in reviews:
            review.profile = profile
            _save_review_object(review=review)

        response_data = api_client.get(reverse(self.profile_reviews_url_name, kwargs={'profile_id': profile.pk})).data

        assert len(response_data) == count_returned_reviews  # type: ignore[arg-type]

    def test_unauthorized_create_review_request(self, api_client: APIClient, profile: Profile):
        """
        Arrange: Профиль пользователя в бд
        Act: Запрос на создание отзыва на профиль
        Assert: 401 ошибка
        """
        _save_profile_object(profile=profile)

        response = api_client.post(reverse(self.profile_reviews_url_name, kwargs={'profile_id': profile.pk}))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        'request_data, status_code',
        (
            (SUCCESS_CREATE_REVIEW_REQUEST_BODY, status.HTTP_201_CREATED),
            ({'rate': 4}, status.HTTP_201_CREATED),
            ({'text': 'Тестовый текст отзыва'}, status.HTTP_400_BAD_REQUEST),
            ({'text': 'Тестовый текст отзыва', 'rate': 0}, status.HTTP_400_BAD_REQUEST),
            ({'text': 'Тестовый текст отзыва', 'rate': 6}, status.HTTP_400_BAD_REQUEST),
        ),
    )
    def test_create_review_request(
        self,
        auth_client: APIClient,
        auth_profile: Profile,
        profile: Profile,
        request_data: dict[str, Any],
        status_code: int,
    ):
        """
        Arrange: Профиль на который будет оставляться отзыв, авторизованный профиль автора отзыва
        Act: Запрос на создание отзыва
        Arrange: Корректный код ответа. В случае успешных запросов -
                 проверка, что в бд создались объекты с корректными данными.
        """
        _save_profile_object(profile=profile)
        _save_profile_object(profile=auth_profile)

        response = auth_client.post(
            path=reverse(self.profile_reviews_url_name, kwargs={'profile_id': profile.pk}),
            data=request_data,
            format='json',
        )

        assert response.status_code == status_code

        if response.status_code == status.HTTP_201_CREATED:
            assert Review.objects.filter(
                profile=profile,
                author=auth_profile,
                text=request_data.get('text', ''),
                rate=request_data.get('rate'),
                is_approved=False,
            ).exists()

    def test_self_review_creation_error(self, auth_client: APIClient, auth_profile: Profile):
        """
        Arrange: Авторизованный пользователь
        Act: Запрос на создание отзыва самому себе
        Asset: 422 ошибка
        """
        response = auth_client.post(
            path=reverse(self.profile_reviews_url_name, kwargs={'profile_id': auth_profile.pk}),
            data=SUCCESS_CREATE_REVIEW_REQUEST_BODY,
            format='json',
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_review_creation_request_if_profile_not_exist(
        self,
        auth_client: APIClient,
        auth_profile: Profile,
    ):
        """
        Arrange: Авторизованный пользователь, айди несуществующего профиля
        Act: Запрос на создание отзыва на несуществующий профиль
        Assert: 404 ошибка
        """
        nonexistent_user_id = auth_profile.pk + 1

        response = auth_client.post(
            path=reverse(self.profile_reviews_url_name, kwargs={'profile_id': nonexistent_user_id}),
            data=SUCCESS_CREATE_REVIEW_REQUEST_BODY,
            format='json',
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteReview:
    """Тесты на вью DeleteReviewAPIView"""

    delete_profile_review_url_name = 'delete_review'

    def test_unauthorized_delete_review_request(self, api_client: APIClient, review_form_unauth_profile: Review):
        """
        Arrange: Навторизованный профиль, отзыв от неавторизованного профиля
        Act: Запрос на удаление отзыва
        Assert: 401 ошибка
        """
        _save_review_object(review=review_form_unauth_profile)

        response = api_client.delete(
            path=reverse(
                self.delete_profile_review_url_name,
                kwargs={
                    'profile_id': review_form_unauth_profile.profile.pk,
                    'review_id': review_form_unauth_profile.pk,
                },
            ),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_review_success_request(self, auth_client: APIClient, review_form_auth_profile: Review):
        """
        Arrange: Авторизованный профиль, отзыв от этого профиля
        Act: Запрос на удаление отзыва
        Assert: Успешное удаление, отзыв существует в бд до запроса и не существует после, код ответа - 200
        """
        _save_review_object(review=review_form_auth_profile)
        review_id = review_form_auth_profile.pk

        assert Review.objects.filter(pk=review_id).exists()

        response = auth_client.delete(
            path=reverse(
                self.delete_profile_review_url_name,
                kwargs={
                    'profile_id': review_form_auth_profile.profile.pk,
                    'review_id': review_id,
                },
            ),
        )

        assert response.status_code == status.HTTP_200_OK
        assert not Review.objects.filter(pk=review_id).exists()
