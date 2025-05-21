from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer, OpenApiExample
from rest_framework import status, serializers, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.misc.custom_auth import CookieTokenAuthentication
from authentication.selectors.profile import get_profile_by_id
from common.swagger.schema import DEFAULT_PRIVATE_API_ERRORS_WITH_404_SCHEMA_RESPONSES, SWAGGER_NO_RESPONSE_BODY
from review.selectors.review import get_visible_reviews
from review.serializers import ReviewSerializer
from review.services.review import delete_review_by_id, recalc_profile_rating

SWAGGER_REVIEWS_TAG = 'Отзывы'


class ProfileReviewsAPIView(APIView):
    """Вью для получения отзывов профиля"""

    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_authentications(self):
        if self.request.method in permissions.SAFE_METHODS:
            return []
        return [CookieTokenAuthentication()]

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

    @extend_schema(
        tags=[SWAGGER_REVIEWS_TAG],
        description='Оставить отзыв',
        request=inline_serializer(
            name='CreateReviewSerializer',
            fields={'text': serializers.CharField(), 'rate': serializers.FloatField()},
        ),
        responses={
            status.HTTP_200_OK: serializer_class(),
            **DEFAULT_PRIVATE_API_ERRORS_WITH_404_SCHEMA_RESPONSES,
            status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(
                description='Unprocessable Entity',
                response='Unprocessable Entity',
                examples=[
                    OpenApiExample(name='422 example', value={'error_detail': 'Нельзя оставить отзыв самому себе'}),
                ],
            ),
        },
    )
    def post(self, request, profile_id: int):
        """Создание отзыва"""
        profile = get_profile_by_id(profile_id)
        author = request.user.profile

        if author.id == profile.id:  # type: ignore[attr-defined]
            return Response(
                data={'error_detail': 'Нельзя оставить отзыв самому себе'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        serializer = self.serializer_class(data={'profile': profile.id, 'author': author.id, **request.data})  # type: ignore[attr-defined]
        serializer.is_valid(raise_exception=True)
        serializer.save()

        recalc_profile_rating(profile_id)

        return Response(status=status.HTTP_201_CREATED)


class DeleteReviewAPIView(APIView):
    """Вью для удаления отзывов"""

    authentication_classes = [CookieTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=[SWAGGER_REVIEWS_TAG],
        description='Оставить отзыв',
        request=inline_serializer(name='CreateReviewSerializer', fields={'text': serializers.CharField()}),
        responses={
            status.HTTP_200_OK: SWAGGER_NO_RESPONSE_BODY,
            **DEFAULT_PRIVATE_API_ERRORS_WITH_404_SCHEMA_RESPONSES,
            status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(
                description='Unprocessable Entity',
                response='Unprocessable Entity',
                examples=[
                    OpenApiExample(
                        name='422 example',
                        value={'error_detail': 'Нельзя удалить чужой отзыв'},
                    ),
                ],
            ),
        },
    )
    def delete(self, request, profile_id: int, review_id: int):
        """Удаление отзыва"""
        profile = get_profile_by_id(profile_id)

        if request.user.profile.id != profile.id:  # type: ignore[attr-defined]
            return Response(
                data={'error_detail': 'Нельзя удалить чужой отзыв'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        delete_review_by_id(review_id)

        return Response(status=status.HTTP_200_OK)
