from typing import Optional

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSet
import structlog

from authentication.misc.custom_auth import CookieTokenAuthentication
from authentication.models import Profile
from booking.models import Advert, Promotion, AdvertStatus
from booking.serializers import AdvertSerializer, SearchFilterSerializer, PromotionSerializer, AdvertCreationSerializer
from booking.services import AdvertService, AdvertsRecommendationService
from common.swagger.schema import DEFAULT_PRIVATE_API_ERRORS_WITH_404_SCHEMA_RESPONSES, SWAGGER_NO_RESPONSE_BODY

logger = structlog.get_logger(__name__)
router = DefaultRouter()

POSTS_SWAGGER_TAG = 'Объявления'


@extend_schema(tags=[POSTS_SWAGGER_TAG])
class AdvertViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [CookieTokenAuthentication]

    queryset = Advert.objects.all()
    serializer_class = AdvertSerializer

    @extend_schema(
        description='Получить объявления пользователя',
        responses={
            status.HTTP_200_OK: serializer_class,
            **DEFAULT_PRIVATE_API_ERRORS_WITH_404_SCHEMA_RESPONSES,
        },
    )
    def list(self, request):
        profile: Profile = get_object_or_404(Profile, user=request.user)  # type: ignore[annotation-unchecked]
        return (
            AdvertsRecommendationService(self.queryset.filter(contact=profile))
            .serialize(self.serializer_class)
            .ok()
            .or_else_404()
        )

    @extend_schema(
        description='Получить конкретное объявление пользователя',
        responses={
            status.HTTP_200_OK: serializer_class,
            **DEFAULT_PRIVATE_API_ERRORS_WITH_404_SCHEMA_RESPONSES,
            status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(description='Unprocessable Entity'),
        },
    )
    def retrieve(self, request, pk=None) -> Optional[Response]:
        profile: Profile = get_object_or_404(Profile, user=request.user)
        return (
            AdvertService.find(
                advert_pk=pk,
                user_profile=profile,
            )
            .serialize(self.serializer_class)
            .ok()
            .or_else_422()
        )

    @extend_schema(
        description='Создать объявление',
        request=serializer_class,
        responses={
            status.HTTP_201_CREATED: serializer_class,
            **DEFAULT_PRIVATE_API_ERRORS_WITH_404_SCHEMA_RESPONSES,
            status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(description='Unprocessable Entity'),
        },
    )
    def create(self, request, *args, **kwargs) -> Optional[Response]:
        logger.debug(
            'auth user data',
            user=request.user,
            data=request.data,
        )

        profile: Profile = get_object_or_404(Profile, user=request.user)
        serializer = AdvertCreationSerializer(data=request.data)

        logger.debug('user got profile', user=request.user, profile=profile)

        if serializer.is_valid():
            data = serializer.validated_data

            logger.debug(
                'got data from user',
                user=request.user,
                data=data,
            )

            return AdvertService.advertise(serializer, contact=profile).created().or_else_422()

        else:
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @extend_schema(
        description='Изменить объявление',
        request=AdvertSerializer,
        responses={
            status.HTTP_200_OK: SWAGGER_NO_RESPONSE_BODY,
            **DEFAULT_PRIVATE_API_ERRORS_WITH_404_SCHEMA_RESPONSES,
            status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(description='Unprocessable Entity'),
        },
    )
    def update(self, request, pk=None) -> Optional[Response]:
        profile: Profile = get_object_or_404(Profile, user=request.user)
        serializer = AdvertSerializer(data=request.data, partial=True)

        if serializer.is_valid():
            return (
                AdvertService.find(
                    advert_pk=pk,
                    user_profile=profile,
                )
                .change(serializer)
                .ok()
                .or_else_422()
            )

        else:
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @extend_schema(  # type: ignore[type-var]
        description='Активировать объявление',
        request={},
        responses={
            status.HTTP_200_OK: SWAGGER_NO_RESPONSE_BODY,
            **DEFAULT_PRIVATE_API_ERRORS_WITH_404_SCHEMA_RESPONSES,
            status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(description='Unprocessable Entity'),
        },
    )
    @action(methods=['patch'], detail=True)  # type: ignore[type-var]
    def activate(self, request, pk=None) -> Optional[Response]:
        profile: Profile = get_object_or_404(Profile, user=request.user)

        return (
            AdvertService.find(
                advert_pk=pk,
                user_profile=profile,
            )
            .activate()
            .ok()
            .or_else_422()
        )

    @extend_schema(  # type: ignore[type-var]
        description='Деактивировать объявление',
        request={},
        responses={
            status.HTTP_200_OK: SWAGGER_NO_RESPONSE_BODY,
            **DEFAULT_PRIVATE_API_ERRORS_WITH_404_SCHEMA_RESPONSES,
            status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(description='Unprocessable Entity'),
        },
    )
    @action(methods=['patch'], detail=True)  # type: ignore[type-var]
    def deactivate(self, request, pk=None) -> Optional[Response]:
        user: Profile = get_object_or_404(Profile, user=request.user)

        return (
            AdvertService.find(
                advert_pk=pk,
                user_profile=user,
            )
            .deactivate()
            .ok()
            .or_else_422()
        )

    @extend_schema(
        description='Удалить объявление',
        request={},
        responses={
            status.HTTP_200_OK: SWAGGER_NO_RESPONSE_BODY,
            **DEFAULT_PRIVATE_API_ERRORS_WITH_404_SCHEMA_RESPONSES,
        },
    )
    def destroy(self, request, pk=None) -> Optional[Response]:
        user: Profile = get_object_or_404(Profile, user=request.user)

        return (
            AdvertService.find(
                advert_pk=pk,
                user_profile=user,
            )
            .delete()
            .ok()
            .or_else_400()
        )


@extend_schema(tags=[POSTS_SWAGGER_TAG])
class AdvertsRecommendationViewSet(ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    queryset = Advert.objects.filter(status=AdvertStatus.ACTIVE)
    serializer_class = AdvertSerializer

    @extend_schema(
        description='Лента объявлений',
        request={},
        responses={
            status.HTTP_200_OK: serializer_class,
            **DEFAULT_PRIVATE_API_ERRORS_WITH_404_SCHEMA_RESPONSES,
        },
    )
    def list(self, request):
        return AdvertsRecommendationService.list().serialize(self.serializer_class).ok().or_else_400()

    @extend_schema(
        description='Объявление из ленты',
        request={},
        responses={
            status.HTTP_200_OK: serializer_class,
            **DEFAULT_PRIVATE_API_ERRORS_WITH_404_SCHEMA_RESPONSES,
        },
    )
    def retrieve(self, request, pk=None):
        return (
            AdvertsRecommendationService(self.queryset.filter(id=pk).values())
            .serialize(self.serializer_class)
            .ok()
            .or_else_404()
        )

    @extend_schema(
        description='Поиск объявлений с фильтрацией',
        parameters=[SearchFilterSerializer],
        responses={
            status.HTTP_200_OK: serializer_class,
            **DEFAULT_PRIVATE_API_ERRORS_WITH_404_SCHEMA_RESPONSES,
            status.HTTP_422_UNPROCESSABLE_ENTITY: OpenApiResponse(description='Unprocessable Entity'),
        },
    )
    @action(detail=False, methods=['get'])
    def filter(self, request):
        serializer = SearchFilterSerializer(data=request.query_params)

        if serializer.is_valid():
            data = serializer.validated_data

            logger.debug(
                'got query params from user`s request',
                user=request.user,
                params=data,
            )

            return (
                AdvertsRecommendationService.ranked_list(serializer).serialize(self.serializer_class).ok().or_else_400()
            )

        else:
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class PromotionViewSet(ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer

    def list(self, request):
        pass

    def retrieve(self, request, pk=None):
        pass

    def create(self, request, *args, **kwargs):
        pass

    def boost(self, request, pk=None):
        pass

    def disable(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass


router.register(r'posts', AdvertViewSet, basename='post')
router.register(r'adverts', AdvertsRecommendationViewSet)
