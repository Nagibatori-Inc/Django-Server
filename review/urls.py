from django.urls import path

from review.views import ProfileReviewsAPIView, DeleteReviewAPIView

urlpatterns = [
    path('profiles/<int:profile_id>/reviews/', ProfileReviewsAPIView.as_view(), name='profile_reviews'),
    path('profiles/<int:profile_id>/reviews/<int:review_id>/', DeleteReviewAPIView.as_view(), name='delete_review'),
]
