from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, User


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):

    if created:
        Profile.objects.create(user=instance)
