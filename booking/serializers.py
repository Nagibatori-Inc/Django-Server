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
    status = serializers.CharField(required=False)
    activated_at = serializers.DateTimeField(required=False)
    created_at = serializers.DateTimeField(required=False)
    contact = AdvertContactSerializer()

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
