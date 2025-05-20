from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.misc.custom_auth import CookieTokenAuthentication
from authentication.selectors.profile import get_profile_by_id
from review.selectors.review import get_visible_reviews
from review.serializers import ReviewSerializer
from review.services.review import delete_review_by_id

SWAGGER_REVIEWS_TAG = 'Отзывы'


class ProfileReviewsListAPIView(APIView):
    """Вью для получения отзывов профиля"""

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = ReviewSerializer

    @extend_schema(
        description='Получить одобренные модерацией отзывы профиля',
        tags=[SWAGGER_REVIEWS_TAG],
        request={},
        responses={
            status.HTTP_200_OK: serializer_class(many=True),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(description='Internal Server Error'),
        },
    )
    def get(self, request, profile_id: int):
        """Получить отзывы профиля"""
        queryset = get_visible_reviews(profile_id)
        return Response(status=status.HTTP_200_OK, data=self.serializer_class(queryset, many=True).data)


@extend_schema(tags=[SWAGGER_REVIEWS_TAG])
class ProfileReviewsAPIView(CreateAPIView):
    """Вью для оставления и удаления отзывов"""

    authentication_classes = [CookieTokenAuthentication]
    permission_classes = [AllowAny]
    serializer_class = ReviewSerializer

    def post(self, request, profile_id: int):
        """Создание отзыва"""
        profile = get_profile_by_id(profile_id)

        if request.user.profile.id == profile.id:  # type: ignore[attr-defined]
            return Response(
                data={'error_detail': 'Нельзя оставить отзыв самому себе'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        serializer = self.serializer_class(data={'profile_id': profile.id, **request.data})  # type: ignore[attr-defined]
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, profile_id: int, review_id: int):
        """Удаление отзыва"""
        profile = get_profile_by_id(profile_id)

        if request.user.profile.id != profile.id:  # type: ignore[attr-defined]
            return Response(
                data={'error_detail': 'Нельзя удалить чужой отзыв'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        delete_review_by_id(review_id)

        return Response(status=status.HTTP_200_OK)
