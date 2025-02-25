from rest_framework import serializers

from booking.models import Advert
from authentication.serializers import ProfileSerializer


class AdvertSerializer(serializers.ModelSerializer):
    contact = ProfileSerializer(required=False)
    class Meta:
        model = Advert
        fields = ['title', 'description', 'price', 'phone']