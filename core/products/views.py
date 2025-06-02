from __future__ import annotations

from rest_framework import generics
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAdminUser

from .models import Plan
from .serializers import PlanSerializer


# Create your views here.

class CreatePlanView(generics.ListCreateAPIView):

    serializer_class = PlanSerializer
    queryset = Plan.objects.all()

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAdminUser()]
