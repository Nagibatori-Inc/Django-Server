from rest_framework import serializers

from booking.models import Advert
from authentication.serializers import ProfileSerializer


class AdvertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advert
        fields = ['title', 'description', 'price', 'phone']


class SearchFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advert
        fields = ['title', 'price']