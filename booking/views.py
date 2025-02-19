from django.shortcuts import render, get_list_or_404
from rest_framework.views import APIView

from booking.models import Advert


class AdvertView(APIView):
    def get(self, request):
        advert_id = request.GET.get('id')
        advert: Advert = get_object_or_404(Advert, pk=advert_id)
        return advert
    
    def post(self, request):
        pass
    
    def put(self, request):
        pass
    
    def delete(self, request):
        pass
