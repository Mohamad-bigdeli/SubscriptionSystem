from __future__ import annotations

import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Profile


User = get_user_model()
class OTPLoginOrSignupSerializer(serializers.Serializer):

    phone = serializers.CharField(max_length=11, required=True)

    def validate(self, attrs):
        phone = attrs.get("phone")
        if phone:
            if not phone.isdigit():
                raise serializers.ValidationError("Invalid phone number.")
            if not phone.startswith("09"):
                raise serializers.ValidationError("Phone must start with 09 digits.")
        return super().validate(attrs)

class OTPLoginOrSignupVerifySerializer(serializers.Serializer):

    phone = serializers.CharField(max_length=11, required=True)
    otp = serializers.CharField(max_length=6, required=True)

    def validate(self, attrs):
        phone = attrs.get("phone")
        otp = attrs.get("otp")
        if otp:
            if not otp.isdigit():
                raise serializers.ValidationError("OTP must be numeric.")
        if phone:
            if not phone.isdigit():
                raise serializers.ValidationError("Invalid phone number.")
            if not phone.startswith("09"):
                raise serializers.ValidationError("Phone must start with 09 digits.")
        return super().validate(attrs)

class CompleteSignUpSerializer(serializers.Serializer):

    email = serializers.EmailField(allow_null=True, allow_blank=True)
    password = serializers.CharField(max_length=255, required=True)
    password1 = serializers.CharField(max_length=255, required=True)

    def validate_password(self, value):

        try:
            validate_password(value)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(list(e.messages))

        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        if not re.search('[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")

        if not re.search('[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")

        if not re.search('[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")

        if not re.search('[^A-Za-z0-9]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")

        return value

    def validate(self, data):
        if data['password'] != data['password1']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return data

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        validate_data = super().validate(attrs)
        validate_data["phone"] = self.user.phone
        validate_data["email"] = self.user.email
        validate_data["user_id"] = self.user.pk
        return validate_data

class UserRelatedSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "phone", "email"]
        read_only_fields = fields

class ProfileSerializer(serializers.ModelSerializer):

    user = UserRelatedSerializer()
    class Meta:
        model = Profile
        fields = [
            "user",
            "id",
            "first_name",
            "last_name",
            "address",
            "postal_code",
            "national_code",
            "created",
            "updated"
        ]
        read_only_fields = ["id", "created", "updated"]

    def validate(self, attrs):
        postal_code = attrs.get("postal_code")
        national_code = attrs.get("national_code")
        if postal_code:
            if len(postal_code) != 10:
                raise serializers.ValidationError("Postal code must be 10 char")
        if national_code:
            if len(national_code) != 9:
                raise serializers.ValidationError("Postal code must be 9 char")
        return super().validate(attrs)

class UserChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(max_length=255, required=True)
    new_password = serializers.CharField(max_length=255, required=True)
    new_password1 = serializers.CharField(max_length=255, required=True)

    def validate_new_password(self, value):

        try:
            validate_password(value)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(list(e.messages))

        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")

        if not re.search('[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")

        if not re.search('[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")

        if not re.search('[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")

        if not re.search('[^A-Za-z0-9]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")

        return value

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password1"):
            raise serializers.ValidationError({"derail": "passwords doesn't match"})
        return super().validate(attrs)
