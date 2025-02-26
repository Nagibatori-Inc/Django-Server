from rest_framework import serializers

from booking.models import Advert, Promotion
from authentication.serializers import ProfileSerializer


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = '__all__'


class AdvertSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer(required=False, read_only=True)
    status = serializers.CharField(required=False)
    activated_at = serializers.DateTimeField(required=False)
    class Meta:
        model = Advert
        fields = ['title', 'description', 'price', 'phone', 'promotion', 'status', 'activated_at']


class SearchFilterSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer(required=False, read_only=True)
    class Meta:
        model = Advert
        fields = ['title', 'price', 'promotion']