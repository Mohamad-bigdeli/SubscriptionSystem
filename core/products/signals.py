from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Plan, Subscription


User = get_user_model()

@receiver(post_save, sender=User)
def create_welcome_subscription(sender, instance, created, **kwargs):
    if created:
        plan = Plan.objects.filter(duration_days=3, price=0).first()
        if plan:
            Subscription.objects.create(user=instance, plan=plan, is_trial=True)
