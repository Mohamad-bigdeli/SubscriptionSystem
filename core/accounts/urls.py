from __future__ import annotations

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views


app_name = "accounts"

urlpatterns = [
    path("otp-login-signup/", views.OTPLoginOrSignupView.as_view(), name="login-signup"),
    path("verify-otp/", views.OTPLoginOrSignupVerifyView.as_view(), name="login-signup-verify"),
    path("complete-signup/", views.CompleteSignUpView.as_view(), name="complete-signup"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("change-password/", views.UserChangePasswordView.as_view(), name="change-password"),

    #jwt
    path("jwt/login/", views.CustomTokenObtainPairView.as_view(), name="jwt-login"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
]
