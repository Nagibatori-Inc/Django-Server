from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import ViewSet

from DjangoServer.utils import HttpMethod
from authentication.models import Profile
from booking.models import Advert
from booking.serializers import AdvertSerializer
from booking.services import AdvertService

router = DefaultRouter()


class AdvertViewSet(ViewSet):
    authentication_classes = (BasicAuthentication, )

    queryset = Advert.objects.all()
    serializer_class = AdvertSerializer
    
    def list(self, request):
        serializer = AdvertSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        advert: Advert = get_object_or_404(Advert, pk=pk)
        serializer = self.serializer_class(advert)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        user: Profile = get_object_or_404(Profile, user=request.user)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            return (
                AdvertService
                .advertise(**data, contact=user)
                .created()
                .or_else_send(status.HTTP_422_UNPROCESSABLE_ENTITY)
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
            .or_else_send(status.HTTP_422_UNPROCESSABLE_ENTITY)
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
            .or_else_send(status.HTTP_422_UNPROCESSABLE_ENTITY)
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
