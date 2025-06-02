from __future__ import annotations

from rest_framework import serializers

from .models import Plan


class PlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = Plan
        fields = [
            "id",
            "duration_days",
            "price",
            "description"
        ]
        read_only_fields = ["id"]
