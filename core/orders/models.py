from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from products.models import Plan


User = get_user_model()

# Create your models here.

class Order(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "pending"),
        ("COMPLETED", "completed"),
        ("CANCELED", "cancelled"),
    )

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="plan")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,11}$', message="Phone number must be entered in the format: '09129876543'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=11)
    city = models.CharField(max_length=100)
    address = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"Order {self.id}"

class Payment(models.Model):

    STATUS_CHOICES = (
        ("PENDING", "pending"),
        ("PAID", "paid"),
        ("FAILED", "failed"),
    )

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="payments")
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="payment")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    amount = models.PositiveIntegerField()
    authority = models.CharField(max_length=100, blank=True)
    ref_id = models.CharField(max_length=100, blank=True, null=True)
    payment_url = models.URLField(blank=True, null=True)
    gateway_response = models.JSONField(default=dict, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.amount != self.order.plan.price:
            raise ValidationError("Payment amount does not match plan price.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.id} for order {self.order.id}"
