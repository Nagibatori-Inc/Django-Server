from django.urls import path

from review.views import ProfileReviewsListAPIView, CreateReviewAPIView, DeleteReviewAPIView

urlpatterns = [
    path('profiles/<int:profile_id>/reviews/', ProfileReviewsListAPIView.as_view(), name='profile_reviews'),
    path('profiles/<int:profile_id>/reviews/', CreateReviewAPIView.as_view(), name='create_review'),
    path('profiles/<int:profile_id>/reviews/<int:review_id>/', DeleteReviewAPIView.as_view(), name='delete_review'),
]
