from __future__ import annotations

from django.urls import path

from . import views


app_name = "orders"

urlpatterns = [
    path("orders/", views.CreateListOrderView.as_view(), name="orders"),
    path("callback/", views.PaymentCallbackView.as_view(), name="callback"),
    path("orders/user/", views.UserOrderPaymentListView.as_view(), name="orders-user")
]
