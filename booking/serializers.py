from rest_framework import serializers

from booking.models import Advert, Promotion


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['type', 'rate', 'status']


class AdvertSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer(required=False, read_only=True)
    status = serializers.CharField(required=False)
    activated_at = serializers.DateTimeField(required=False)
    created_at = serializers.DateTimeField(required=False)

    def create(self, validated_data):
        return Advert.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    class Meta:
        model = Advert
        fields = '__all__'


class SearchFilterSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    min_price = serializers.IntegerField(required=False)
    max_price = serializers.IntegerField(required=False)

    class Meta:
        model = Advert
        fields = ['title', 'location', 'min_price', 'max_price']
