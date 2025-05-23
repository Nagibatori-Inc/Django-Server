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


class TestProfilesReview:

    profile_reviews_url_name = 'profile_reviews'

    @classmethod
    def _save_profile_object(cls, profile: Profile) -> None:
        profile.user.save()
        profile.save()

    @classmethod
    def _save_review_object(cls, review: Review) -> None:
        cls._save_profile_object(profile=review.profile)
        cls._save_profile_object(profile=review.author)
        review.save()

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
        self._save_profile_object(profile=profile)
        for review in reviews:
            review.profile = profile
            self._save_review_object(review=review)

        response_data = api_client.get(reverse(self.profile_reviews_url_name, kwargs={'profile_id': profile.pk})).data

        assert len(response_data) == count_returned_reviews

    def test_unauthorized_create_review_request(self, api_client: APIClient, profile: Profile):
        """
        Arrange: Профиль пользователя в бд
        Act: Запрос на создание отзыва на профиль
        Assert: 401 ошибка
        """
        self._save_profile_object(profile=profile)

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
        self._save_profile_object(profile=profile)
        self._save_profile_object(profile=auth_profile)

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
