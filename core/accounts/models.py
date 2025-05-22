from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from django.core.validators import RegexValidator

# Create your models here.

class User(AbstractBaseUser, PermissionsMixin):

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,11}$', message="Phone number must be entered in the format: '09129876543'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=11, unique=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)   
    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "phone"

    objects = UserManager()

    def __str__(self):
        return self.phone

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name="profile", null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    national_code = models.CharField(max_length=9, null=True, blank=True)

    def __str__(self):
        return self.user.phone
