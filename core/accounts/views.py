from rest_framework import generics
from rest_framework.response import Response
from .serializers import OTPLoginOrSignupSerializer, OTPLoginOrSignupVerifySerializer, CompleteSignUpSerializer, CustomTokenObtainPairSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.cache import cache
from rest_framework import status
import random
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.

class OTPLoginOrSignupView(generics.GenericAPIView):

    permission_classes = [AllowAny]
    serializer_class = OTPLoginOrSignupSerializer

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
                "refresh_token":str(refresh),
                "access_token":str(access)
            },
            status=status.HTTP_200_OK
        )

class CompleteSignUpView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = CompleteSignUpSerializer

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