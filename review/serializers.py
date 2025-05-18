from rest_framework import serializers

from review.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов"""

    class Meta:
        model = Review
        fields = ['profile', 'author', 'text', 'created_at']
