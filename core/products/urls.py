from __future__ import annotations

from django.urls import path

from . import views


app_name = "products"

urlpatterns = [
    path("plan/", views.CreatePlanView.as_view(), name="plans")
]
