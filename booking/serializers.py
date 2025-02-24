from rest_framework import serializers

from booking.models import Advert


class AdvertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advert
        fields = ['title', 'description', 'price', 'phone']