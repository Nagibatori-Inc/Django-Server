from rest_framework import serializers

from booking.models import Advert, Promotion


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = '__all__'


class AdvertSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer(required=False, read_only=True)
    status = serializers.CharField(required=False)
    activated_at = serializers.DateTimeField(required=False)
    created_at = serializers.DateTimeField(required=False)
    class Meta:
        model = Advert
        fields = '__all__'


class SearchFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advert
        fields = ['title', 'price']