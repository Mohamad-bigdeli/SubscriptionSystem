from rest_framework import serializers
import re
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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