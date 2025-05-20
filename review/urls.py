from django.urls import path

from review.views import ProfileReviewsListAPIView, ProfileReviewsAPIView

urlpatterns = [
    path('profiles/<int:profile_id>/reviews/', ProfileReviewsListAPIView.as_view(), name='profile_reviews'),
    path('profiles/<int:profile_id>/reviews/', ProfileReviewsAPIView.as_view(), name='profile_reviews'),
]
