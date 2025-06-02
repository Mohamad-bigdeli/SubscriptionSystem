from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


User = get_user_model()

# Create your models here.

class Plan(models.Model):
    DURATION_CHOICES = (
        (3, "3 Days"),
        (30, "30 Days"),
        (90, "90 Days"),
        (180, "180 Days"),
        (360, "360 Days")
    )
    duration_days = models.IntegerField(choices=DURATION_CHOICES)
    price = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.duration_days} days"

class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'ACTIVE'),
        ('expired', 'EXPIRED'),
        ('canceled', 'CANCELED'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_trial = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["end_date"]),
        ]

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    def is_active_subscription(self):
        return self.status == 'active' and self.end_date > timezone.now()

    def __str__(self):
        return f"{self.user.phone} - {self.plan.duration_days} days ({self.status})"
