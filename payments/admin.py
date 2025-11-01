"""
Admin configuration for payments module.
"""
from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'folio', 'amount', 'payment_method',
        'status', 'created_at', 'completed_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = [
        'folio__guest__name', 'stripe_payment_intent_id',
        'mpesa_transaction_id'
    ]
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
