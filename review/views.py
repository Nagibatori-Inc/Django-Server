from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from review.selectors.review import get_visible_reviews
from review.serializers import ReviewSerializer


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
