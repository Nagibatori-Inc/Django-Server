from rest_framework import serializers

from support.models import SupportMessage, SupportAnswer


class SupportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = ["subject", "message"]


class SupportAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportAnswer
        fields = ["answer"]
