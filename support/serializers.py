from rest_framework import serializers

from support.models import SupportMessage, SupportAnswer


class SupportMessageSerializerIn(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = ["subject", "message"]


class SupportMessageSerializerOut(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = ["subject", "message", "answers"]


class SupportAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportAnswer
        fields = ["answer"]
