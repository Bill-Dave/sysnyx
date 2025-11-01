"""
DRF serializers for payments module.
"""
from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    
    class Meta:
        model = Payment
        fields = [
            'id', 'folio', 'amount', 'payment_method', 'status',
            'stripe_payment_intent_id', 'mpesa_transaction_id',
            'metadata', 'error_message',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'status', 'stripe_payment_intent_id',
            'error_message', 'created_at', 'updated_at', 'completed_at'
        ]


class CreatePaymentSerializer(serializers.Serializer):
    """Serializer for creating a payment."""
    folio_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    payment_method = serializers.ChoiceField(choices=['stripe', 'mpesa', 'cash', 'card'])
    stripe_token = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False, default=dict)
