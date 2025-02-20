from django.shortcuts import render, get_list_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status

from booking.models import Advert
from booking.service import AdvertService


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
        # Пока проверка на валидность данныз из тела запроса не происходит
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
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, body=advert)
        
        return Response(status=status.HTTP_201_CREATED, body={'message': 'OK'})
    
    def put(self, request):
        data_to_change = request.data.get('changed_data', {})
        user: User = request.user    
        
        advert = get_object_or_404(Advert, phone=user.phone)
        advert_service = AdvertService(advert)
        
        advert_service.change(data_to_change)
        
        return Response(status=status.HTTP_200_OK, body={'message': f'Advert {advert.id} successfully changed'})
    
    def delete(self, request):
        pass
