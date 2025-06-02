from __future__ import annotations

import random

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from rest_framework import generics, mixins, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Profile
from .serializers import (
    CompleteSignUpSerializer,
    CustomTokenObtainPairSerializer,
    OTPLoginOrSignupSerializer,
    OTPLoginOrSignupVerifySerializer,
    ProfileSerializer,
    UserChangePasswordSerializer,
)


User = get_user_model()

# Create your views here.

class OTPLoginOrSignupView(generics.GenericAPIView):

    permission_classes = [AllowAny]
    serializer_class = OTPLoginOrSignupSerializer

    @ratelimit(key='user_or_ip', rate='5/m', method='POST', block=True)
    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        if not phone:
            return Response({"detail":"Phone number is required!"}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"otp:{phone}"
        if cache.get(cache_key):
            return Response({"detail":"Please wait before requesting again."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        otp = str(random.randint(100000, 999999))
        cache.set(cache_key, otp, timeout=120)

        print(f"Send OTP {otp} to phone {phone}")

        return Response({"detail":"OTP sent successfully."}, status=status.HTTP_200_OK)

class OTPLoginOrSignupVerifyView(generics.GenericAPIView):

    permission_classes = [AllowAny]
    serializer_class = OTPLoginOrSignupVerifySerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        otp = serializer.validated_data["otp"]

        if not phone or not otp:
            return Response({"detail":"Both phone and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"otp:{phone}"
        cached_otp = cache.get(cache_key)
        if not cached_otp:
            return Response({"detail":"OTP code has be expired try again"}, status=status.HTTP_400_BAD_REQUEST)
        if otp != cached_otp:
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        user, _ = User.objects.get_or_create(phone=phone)

        access = AccessToken.for_user(user=user)
        refresh = RefreshToken.for_user(user=user)

        cache.delete(cache_key)

        return Response(
            {
                "id":user.id,
                "phone":user.phone,
                "email":user.email,
                "refresh_token":str(refresh),
                "access_token":str(access)
            },
            status=status.HTTP_200_OK
        )

class CompleteSignUpView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = CompleteSignUpSerializer

    @ratelimit(key='user_or_ip', rate='10/m', method='POST', block=True)
    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = request.user

        user.email = email
        user.set_password(password)
        user.save()

        return Response({"detail":"SignUp complete successfully."}, status=status.HTTP_200_OK)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @ratelimit(key='user_or_ip', rate='5/m', method='POST', block=True)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
class ProfileView(generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):

    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return Profile.objects.select_related("user").get(user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class UserChangePasswordView(generics.GenericAPIView):
    serializer_class = UserChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)

    @ratelimit(key='user_or_ip', rate='5/m', method='POST', block=True)
    def put(self, request, *args, **kwargs):

        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"detail": "The old password is wrong!"}, status=status.HTTP_400_BAD_REQUEST,)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"detail": "Change password successfully"}, status=status.HTTP_200_OK)
