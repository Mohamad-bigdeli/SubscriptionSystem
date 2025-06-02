from __future__ import annotations

from django.db import transaction
from django.shortcuts import redirect
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import extend_schema
from products.models import Plan, Subscription
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from utils.zarinpal_client import ZarinpalClient

from .models import Order, Payment
from .serializers import (
    OrderDetailSerializer,
    OrderSerializer,
    UserOrderPaymentListSerializer,
)


# Create your views here.

class CreateListOrderView(generics.GenericAPIView):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @ratelimit(key='user_or_ip', rate='5/m', method='POST', block=True)
    @transaction.atomic()
    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            if Subscription.objects.filter(user=request.user, status="ACTIVE").exists():
                return Response({"detail":"you have ready subscription"}, status=status.HTTP_400_BAD_REQUEST)

            validated_data = serializer.validated_data
            plan = validated_data["plan"]
            if not plan:
                return Response({"detail":"this plan is not exist"}, status=status.HTTP_400_BAD_REQUEST)

            order = Order.objects.create(
                user=request.user,
                plan=plan,
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                phone=validated_data["phone"],
                city=validated_data["city"],
                address=validated_data["address"],
                status="PENDING",
            )

            payment = Payment.objects.create(
                user=request.user,
                order=order,
                status="PENDING",
                amount=plan.price
                )
            zarinpal = ZarinpalClient()
            response = zarinpal.request_payment(
                            amount=plan.price,
                            callback_url="http://127.0.0.1:8000/api/v1/payments/callback/",
                            mobile=validated_data["phone"],
                            description=f"Payment for order {order.id}"
                        )
            payment.authority = response.get("authority")
            payment.payment_url = response.get("payment_url")
            payment.gateway_response = response["raw_response"]
            payment.save()

            Subscription.objects.create(user=request.user, plan=plan, status="CANCELED", is_trial=False)

            return Response(OrderDetailSerializer(order).data, status=status.HTTP_200_OK)

        except Plan.DoesNotExist:
            return Response({"detail": "This plan does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Error creating order: {e!s}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(exclude=True)
class PaymentCallbackView(generics.GenericAPIView):

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        authority = request.query_params.get("Authority")
        status = request.query_params.get("Status")

        if not authority or status != "OK":
            return redirect("http://bahoosh360.ir/payment/failed/")

        try:
            payment = Payment.objects.get(authority=authority)
            zarinpal = ZarinpalClient()
            result = zarinpal.verify_payment(authority, payment.amount)

            payment.status = "PAID" if result["raw_response"]["data"]["code"] in [100, 101] else "FAILED"
            payment.ref_id = result.get("ref_id")
            payment.payment_date = timezone.now()
            payment.gateway_response = result["raw_response"]
            payment.save()

            if payment.status == "PAID":
                payment.order.status = "COMPLETED"
                payment.order.save()
                subscription = Subscription.objects.get(user=payment.user)
                subscription.status = "ACTIVE"
                subscription.save()
                return redirect("http://bahoosh360.ir/payment/success/")
            payment.order.status = "CANCELED"
            payment.order.save()
            return redirect("http://bahoosh360.ir/payment/failed/")
        except Payment.DoesNotExist:
            return redirect("http://bahoosh360.ir/payment/failed/")
        except Exception:
            return redirect("http://bahoosh360.ir/payment/failed/")

class UserOrderPaymentListView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = UserOrderPaymentListSerializer

    def get_queryset(self):
            return Payment.objects.select_related("order__plan").filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception:
            return Response({"error": "An error occurred while fetching payments."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
