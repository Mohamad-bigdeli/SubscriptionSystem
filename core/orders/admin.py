from __future__ import annotations

import json

from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import Order, Payment


User = get_user_model()

class PaymentAdminForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'

    def clean_gateway_response(self):
        data = self.cleaned_data['gateway_response']
        if data and not isinstance(data, dict):
            try:
                json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError("فیلد gateway_response باید یک JSON معتبر باشد.")
        return data

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user_link',
        'plan_link',
        'first_name',
        'last_name',
        'phone',
        'city',
        'status',
        'created',
        'updated',
        'payment_status',
    )
    list_filter = (
        'status',
        'created',
        'updated',
        'plan',
        'city',
        'user',
    )
    search_fields = (
        'id',
        'first_name',
        'last_name',
        'phone',
        'user__phone',
        'user__email',
        'address',
    )
    list_editable = ('status',)
    readonly_fields = ('created', 'updated', 'user', 'payment_link')
    list_per_page = 25
    date_hierarchy = 'created'
    ordering = ('-created',)
    actions = ['cancel_orders', 'mark_as_completed']

    def user_link(self, obj):
        app_label = User._meta.app_label
        model_name = User._meta.model_name
        url = reverse(f'admin:{app_label}_{model_name}_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.phone or obj.user.email or obj.user.username)
    user_link.short_description = 'کاربر'

    def plan_link(self, obj):
        """
        لینک به پلن در ادمین با استفاده از __str__ به‌جای name
        """
        url = reverse('admin:products_plan_change', args=[obj.plan.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.plan) or obj.plan.id)
    plan_link.short_description = 'پلن'

    def payment_status(self, obj):
        try:
            payment = obj.payment
            color = {
                'PAID': 'green',
                'PENDING': 'orange',
                'FAILED': 'red',
            }.get(payment.status, 'black')
            return format_html('<span style="color: {}">{}</span>', color, payment.status)
        except Payment.DoesNotExist:
            return format_html('<span style="color: red">بدون پرداخت</span>')
    payment_status.short_description = 'وضعیت پرداخت'

    def payment_link(self, obj):
        try:
            payment = obj.payment
            url = reverse('admin:orders_payment_change', args=[payment.id])
            return format_html('<a href="{}">پرداخت {}</a>', url, payment.id)
        except Payment.DoesNotExist:
            return 'بدون پرداخت'
    payment_link.short_description = 'پرداخت'

    def cancel_orders(self, request, queryset):
        updated = queryset.update(status='CANCELED')
        self.message_user(request, f"{updated} سفارش با موفقیت لغو شدند.", messages.SUCCESS)
    cancel_orders.short_description = 'لغو سفارش‌های انتخاب‌شده'

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f"{updated} سفارش با موفقیت به‌عنوان تکمیل‌شده علامت‌گذاری شدند.", messages.SUCCESS)
    mark_as_completed.short_description = 'علامت‌گذاری به‌عنوان تکمیل‌شده'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('plan',)
        return self.readonly_fields

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentAdminForm
    list_display = (
        'id',
        'order_link',
        'user_link',
        'status',
        'amount',
        'authority',
        'ref_id',
        'payment_date',
        'created',
        'payment_url_link',
    )
    list_filter = (
        'status',
        'created',
        'payment_date',
        'order__plan',
        'user',
    )
    search_fields = (
        'id',
        'order__id',
        'user__phone',
        'user__email',
        'authority',
        'ref_id',
    )
    readonly_fields = (
        'created',
        'updated',
        'gateway_response_display',
        'order_link',
        'user_link',
        'payment_url_link',
    )
    list_editable = ('status',)
    list_per_page = 25
    date_hierarchy = 'created'
    ordering = ('-created',)
    actions = ['mark_as_failed', 'mark_as_paid']

    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">سفارش {}</a>', url, obj.order.id)
    order_link.short_description = 'سفارش'

    def user_link(self, obj):
        app_label = User._meta.app_label
        model_name = User._meta.model_name
        url = reverse(f'admin:{app_label}_{model_name}_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.phone or obj.user.email or obj.user.username)
    user_link.short_description = 'کاربر'

    def payment_url_link(self, obj):
        if obj.payment_url:
            return format_html('<a href="{}" target="_blank">مشاهده</a>', obj.payment_url)
        return '-'
    payment_url_link.short_description = 'لینک پرداخت'

    def gateway_response_display(self, obj):
        if obj.gateway_response:
            return format_html(
                '<pre style="white-space: pre-wrap;">{}</pre>',
                json.dumps(obj.gateway_response, indent=2, ensure_ascii=False)
            )
        return 'بدون پاسخ'
    gateway_response_display.short_description = 'پاسخ دروازه پرداخت'

    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='FAILED')
        self.message_user(request, f"{updated} پرداخت با موفقیت به‌عنوان ناموفق علامت‌گذاری شدند.", messages.SUCCESS)
    mark_as_failed.short_description = 'علامت‌گذاری به‌عنوان ناموفق'

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='PAID', payment_date=timezone.now())
        self.message_user(request, f"{updated} پرداخت با موفقیت به‌عنوان موفق علامت‌گذاری شدند.", messages.SUCCESS)
    mark_as_paid.short_description = 'علامت‌گذاری به‌عنوان موفق'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('order', 'user', 'authority', 'ref_id')
        return self.readonly_fields
