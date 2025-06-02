from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import Profile, User


class CustomUserAdmin(UserAdmin):

    model = User
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = (
        "phone",
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    list_filter = (
        "phone",
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    searching_fields = ("phone",)
    ordering = ("phone",)
    filter_horizontal = []
    fieldsets = (
        (
            "Authentication",
            {
                "fields": ("phone", "password"),
            },
        ),
        (
            "permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                ),
            },
        ),
        (
            "group permissions",
            {
                "fields": ("groups", "user_permissions"),
            },
        ),
        (
            "important date",
            {
                "fields": ("last_login",),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                ),
            },
        ),
    )
admin.site.register(User, CustomUserAdmin)

admin.site.register(Profile)
