from django.urls import path

from review.views import ProfileReviewsListAPIView

urlpatterns = [
    path('profiles/<int:profile_id>/reviews', ProfileReviewsListAPIView.as_view(), name='profile_reviews'),
]
