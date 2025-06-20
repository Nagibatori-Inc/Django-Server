from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["advert", "service_provider"]


class WebHookEventSerializer(serializers.Serializer):
    event = serializers.CharField()
    object = serializers.JSONField()
