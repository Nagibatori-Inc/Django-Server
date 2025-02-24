from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.routers import DefaultRouter

from authentication.models import Profile
from booking.models import Advert
from booking.service import AdvertService

from http import HTTPMethod

router = DefaultRouter()


class AdvertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advert
        fields = ['title', 'description', 'price', 'phone']


class AdvertViewSet(ModelViewSet):
    @action(methods=HTTPMethod.GET, detail=True)
    def list(self, request):
        queryset = Advert.objects.all()
        serializer_class = AdvertSerializer(queryset, many=True)
        return Response(serializer_class.data)

    @action(methods=HTTPMethod.POST, detail=True)
    def create(self, request, *args, **kwargs):
        user: Profile = get_object_or_404(Profile, user=request.user)
        serializer = AdvertSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            return (
                AdvertService
                .advertise(**data)
                .ok()
                .or_else_send(status.HTTP_422_UNPROCESSABLE_ENTITY)
            )


class AdvertView(APIView):
    def get(self, request): # TODO: из request'а будем доставать юзера, дабы проверять есть ли у него вообще заявленное объявление
        user: User = request.user
        
        advert_id = request.GET.get('id')
        advert: Advert = get_object_or_404(Advert, pk=advert_id)
        
        return advert
    
    def post(self, request):
        user: User = request.user
        
        # TODO: Нужны будут схемы на body ВСЕХ POST и PUT запросов дабы не доставать по одному полю для создания модельки 
        # а целиком модель из схемы, например, хоть те же сериализаторы
        # Пока проверка на валидность данных из тела запроса не происходит
        advert: dict = request.data.get('advert')
        
        # TODO: А также пока не происходит проверки на наличие данных
        # В дальнейшем через документацию для АПИ OpenAPI указываем required fields в теле запроса
        # КСТАТИ, есть ли в rest framework встроенная, например, через тот же OpenAPI поверка required полей тела запроса???
        advert_service: AdvertService = AdvertService.advertise(
            title=advert.get('title'),
            description=advert.get('description'),
            price=advert.get('price'),
            phone=advert.get('phone'),
            promotion=advert.get('promotion'),
        )
        
        if not advert_service.advert:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data=advert)
        
        return Response(status=status.HTTP_201_CREATED, data={'message': 'OK'})
    
    def put(self, request):
        data_to_change = request.data.get('changed_data', {})
        user: User = request.user    
        
        advert = get_object_or_404(Advert, phone=user.phone)
        advert_service = AdvertService(advert)
        
        advert_service.change(data_to_change)
        
        return Response(status=status.HTTP_200_OK, data={'message': f'Advert {advert.id} successfully changed'})
    
    def delete(self, request):
        user: User = request.user
        
        advert = get_object_or_404(Advert, phone=user.phone)
        advert_service = AdvertService(advert)
        
        advert_service.remove()
        
        return Response(status=status.HTTP_200_OK, data={'message': f'Advert successfully removed'})
