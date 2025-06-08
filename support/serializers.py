from rest_framework import serializers

from support.models import SupportMessage


class SupportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = ["subject", "message"]
