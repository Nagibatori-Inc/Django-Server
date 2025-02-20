from django.urls import path
from knox.views import LogoutView, LogoutAllView

from authentication.views import SignUpView, ProfileView, LoginView

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/logout_all/", LogoutAllView.as_view(), name="logout-all"),
    path("auth/sign_up/", SignUpView.as_view(), name="sign-up"),
    path("profiles/<int:pk>", ProfileView.as_view(), name="profile-details")
]
