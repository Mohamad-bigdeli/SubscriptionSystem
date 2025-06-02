from __future__ import annotations

from django.utils import timezone
from rest_framework.permissions import BasePermission

from .models import Subscription


class HasValidSubscription(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        subs = Subscription.objects.filter(user=request.user, status='ACTIVE')
        for sub in subs:
            if sub.end_date < timezone.now():
                sub.status = 'expired'
                sub.save()
            else:
                return True
        return False
