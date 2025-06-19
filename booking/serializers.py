from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from authentication.models import Profile
from booking.models import Advert, Promotion, AdvertImage


class AdvertContactSerializer(serializers.Serializer):
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = Profile

    def get_name(self, obj: Profile) -> str:
        return obj.name

    def get_username(self, obj: Profile) -> str:
        return obj.user.username

    def get_first_name(self, obj: Profile) -> str:
        return obj.user.first_name

    def get_email(self, obj: Profile) -> str:
        return obj.user.email


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['type', 'rate', 'status']


class AdvertImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)

    class Meta:
        model = AdvertImage
        fields = ['image']


class AdvertSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer(required=False, read_only=True)
    images = AdvertImageSerializer(many=True, required=False, read_only=True)
    logo = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Advert
        fields = '__all__'


class AdvertCreationSerializer(serializers.ModelSerializer):
    images = AdvertImageSerializer(many=True, read_only=True)
    logo = Base64ImageField(required=True)

    def create(self, validated_data):
        images = [image.save() for image in validated_data.pop('images', [])]
        return Advert.objects.create(**validated_data, images=images)

    class Meta:
        model = Advert
        fields = ['title', 'description', 'price', 'phone', 'location', 'status', 'logo', 'images']


class SearchFilterSerializer(serializers.ModelSerializer):
    min_price = serializers.IntegerField(required=False)
    max_price = serializers.IntegerField(required=False)

    class Meta:
        model = Advert
        fields = ['title', 'location', 'min_price', 'max_price']
