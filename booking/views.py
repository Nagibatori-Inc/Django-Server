from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSet
import structlog

from DjangoServer.utils import HttpMethod
from authentication.models import Profile
from booking.models import Advert, AdvertStatus
from booking.serializers import AdvertSerializer, SearchFilterSerializer
from booking.services import AdvertService, AdvertsRecommendationService

logger = structlog.get_logger(__name__)
router = DefaultRouter()


class AdvertViewSet(ViewSet):
    authentication_classes = (BasicAuthentication, )

    queryset = Advert.objects.all()
    serializer_class = AdvertSerializer
    
    def list(self, request):
        return (
            AdvertsRecommendationService
            .list()
            .serialize(self.serializer_class)
            .ok()
            .or_else_400()
        )

    @action(detail=False, methods=[HttpMethod.GET])
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
                AdvertsRecommendationService
                .ranked_list(serializer)
                .serialize(self.serializer_class)
                .ok()
                .or_else_400()
            )

        else:
            return Response(
                serializer.errors,
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

    def retrieve(self, request, pk=None):
        profile: Profile = get_object_or_404(Profile, user=request.user)
        return (
            AdvertService
            .find(
                advert_pk=pk,
                user_profile=profile,
            )
            .serialize(self.serializer_class)
            .ok()
            .or_else_422()
        )

    def create(self, request, *args, **kwargs):
        logger.debug(
            'auth user data',
            user=request.user,
            data=request.data,
        )

        profile: Profile = get_object_or_404(Profile, user=request.user)
        serializer = self.serializer_class(data=request.data)

        logger.debug(
            'user got profile',
            user=request.user,
            profile=profile
        )

        if serializer.is_valid():
            data = serializer.validated_data

            logger.debug(
                'got data from user',
                user=request.user,
                data=data,
            )

            return (
                AdvertService
                .advertise(serializer, contact=profile)
                .created()
                .or_else_422()
            )

        else:
            return Response(
                serializer.errors,
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

    def update(self, request, pk=None):
        pass

    @action(methods=[HttpMethod.PATCH], detail=True)
    def activate(self, request, pk=None):
        profile: Profile = get_object_or_404(Profile, user=request.user)

        return (
            AdvertService
            .find(
                advert_pk=pk,
                user_profile=profile,
            )
            .activate()
            .ok()
            .or_else_422()
        )

    @action(methods=[HttpMethod.PATCH], detail=True)
    def deactivate(self, request, pk=None):
        user: Profile = get_object_or_404(Profile, user=request.user)

        return (
            AdvertService
            .find(
                advert_pk=pk,
                user_profile=user,
            )
            .deactivate()
            .ok()
            .or_else_422()
        )

    def destroy(self, request, pk=None):
        pass
    
    
advert_list = AdvertViewSet.as_view({
    HttpMethod.GET: 'list',
    HttpMethod.POST: 'create',
    HttpMethod.PUT: 'update',
    HttpMethod.PATCH: 'activate',
    HttpMethod.DELETE: 'destroy',
})

router.register(r'adverts', AdvertViewSet)
