from __future__ import annotations

from accounts.serializers import UserRelatedSerializer
from products.models import Plan
from products.serializers import PlanSerializer
from rest_framework import serializers

from .models import Order, Payment


class OrderSerializer(serializers.ModelSerializer):

    plan = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all())

    class Meta:
        model = Order
        fields = [
            "plan",
            "first_name",
            "last_name",
            "phone",
            "city",
            "address",
            "status",
            "created",
            "updated",
        ]
        read_only_fields = ["user", "status", "created", "updated"]

    def validate(self, attrs):
        plan = attrs.get("plan")
        if plan.id == 1:
            raise serializers.ValidationError("This plan is not available")
        return super().validate(attrs)

class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "amount",
            "authority",
            "payment_url",
            "gateway_response",
            "created",
            "updated"
        ]
        read_only_fields = fields

class OrderDetailSerializer(serializers.ModelSerializer):

    payment = PaymentSerializer()
    user = UserRelatedSerializer()
    plan = PlanSerializer()

    class Meta:
        model = Order
        fields = [
            "id",
            "payment",
            "plan",
            "user",
            "first_name",
            "last_name",
            "phone",
            "address",
            "city",
            "status",
            "created",
            "updated",
        ]
        read_only_fields = fields

class UserOrderPaymentListSerializer(serializers.ModelSerializer):

    order = OrderSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "amount",
            "ref_id",
            "payment_date",
            "order",
        ]
        read_only_fields = fields
