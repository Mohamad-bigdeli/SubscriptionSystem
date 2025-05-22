from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("otp-login-signup/", views.OTPLoginOrSignupView.as_view(), name="login-signup"),
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login"),
    path("verify/", views.OTPLoginOrSignupVerifyView.as_view(), name="login-signup-verify"),
    path("complete/", views.CompleteSignUpView.as_view(), name="complete-signup")
]