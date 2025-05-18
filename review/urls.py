from django.urls import path

from review.views import ProfileReviewsAPIView

urlpatterns = [
    path('profiles/<int:profile_id>/reviews', ProfileReviewsAPIView.as_view(), name='profile_reviews'),
]
