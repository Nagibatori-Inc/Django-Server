from typing import Optional

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSet
import structlog

from authentication.models import Profile
from booking.models import Advert, Promotion
from booking.serializers import AdvertSerializer, SearchFilterSerializer, PromotionSerializer
from booking.services import AdvertService, AdvertsRecommendationService

logger = structlog.get_logger(__name__)
router = DefaultRouter()


class AdvertViewSet(ViewSet):
    authentication_classes = (BasicAuthentication,)

    queryset = Advert.objects.all()
    serializer_class = AdvertSerializer

    def list(self, request):
        pass

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

    def create(self, request, *args, **kwargs) -> Optional[Response]:
        logger.debug(
            'auth user data',
            user=request.user,
            data=request.data,
        )

        profile: Profile = get_object_or_404(Profile, user=request.user)
        serializer = self.serializer_class(data=request.data)

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

    def update(self, request, pk=None) -> Optional[Response]:
        profile: Profile = get_object_or_404(Profile, user=request.user)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data

            return (
                AdvertService.find(
                    advert_pk=pk,
                    user_profile=profile,
                )
                .change(data)
                .ok()
                .or_else_422()
            )

        else:
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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


class AdvertsRecommendationViewSet(ViewSet):
    queryset = Advert.objects.all()
    serializer_class = AdvertSerializer

    def list(self, request):
        return AdvertsRecommendationService.list().serialize(self.serializer_class).ok().or_else_400()

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
    authentication_classes = (BasicAuthentication,)

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
