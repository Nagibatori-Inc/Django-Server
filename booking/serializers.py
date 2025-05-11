from rest_framework import serializers

from authentication.models import Profile
from booking.models import Advert, Promotion


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


class AdvertSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer(required=False, read_only=True)

    class Meta:
        model = Advert
        fields = '__all__'


class AdvertCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advert
        fields = ['title', 'description', 'price', 'location', 'status']


class SearchFilterSerializer(serializers.ModelSerializer):
    min_price = serializers.IntegerField(required=False)
    max_price = serializers.IntegerField(required=False)

    class Meta:
        model = Advert
        fields = ['title', 'location', 'min_price', 'max_price']
