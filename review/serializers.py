from rest_framework import serializers

from review.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов"""

    class Meta:
        model = Review
        fields = ['profile', 'author', 'text', 'created_at', 'rate']


class ModerateReviewSerializer(serializers.Serializer):
    """Сериализатор для обработки запроса на модерацию отзыва"""

    review_id = serializers.PrimaryKeyRelatedField(queryset=Review.objects.filter(is_approved=False), help_text='Отзыв')
    is_approved = serializers.BooleanField(help_text='Одобрен')
