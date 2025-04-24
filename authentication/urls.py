from django.urls import path, include
from knox.views import LogoutView, LogoutAllView
from rest_framework.routers import DefaultRouter

from authentication.views import (
    SignUpView,
    ProfileViewSet,
    LoginView,
    ProfileVerificationView,
    SendVerificationCodeView,
    ResetPasswordValidateTokenView,
    ResetPasswordConfirmView,
)

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet, basename="profile")
urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/logout_all/", LogoutAllView.as_view(), name="logout-all"),
    path("auth/sign_up/", SignUpView.as_view(), name="sign-up"),
    path("auth/send_code/", SendVerificationCodeView.as_view(), name="send-code"),
    path("auth/verify/", ProfileVerificationView.as_view(), name="profile-verification"),
    path("auth/validate/", ResetPasswordValidateTokenView.as_view(), name="otp-validation"),
    path("auth/reset_password/", ResetPasswordConfirmView.as_view(), name="password-reset"),
    path("", include(router.urls)),
]
