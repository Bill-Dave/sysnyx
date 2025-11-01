"""
DRF serializers for billing module.
"""
from rest_framework import serializers
from .models import Guest, Folio, Charge, GuestSession


class GuestSerializer(serializers.ModelSerializer):
    """Serializer for Guest model."""
    
    class Meta:
        model = Guest
        fields = [
            'id', 'name', 'email', 'phone', 'room_number',
            'check_in', 'check_out', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChargeSerializer(serializers.ModelSerializer):
    """Serializer for Charge model."""
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = Charge
        fields = [
            'id', 'service', 'service_name', 'description',
            'quantity', 'base_amount', 'final_amount',
            'breakdown', 'created_at', 'created_by'
        ]
        read_only_fields = [
            'id', 'base_amount', 'final_amount', 'breakdown', 'created_at'
        ]


class FolioSerializer(serializers.ModelSerializer):
    """Serializer for Folio model with nested charges."""
    guest = GuestSerializer(read_only=True)
    charges = ChargeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Folio
        fields = [
            'id', 'guest', 'status', 'total_charges',
            'total_payments', 'balance', 'charges',
            'created_at', 'updated_at', 'settled_at'
        ]
        read_only_fields = [
            'id', 'total_charges', 'total_payments', 'balance',
            'created_at', 'updated_at'
        ]


class AddChargeSerializer(serializers.Serializer):
    """Serializer for adding charges to a folio."""
    service_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)
    extras = serializers.JSONField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)
    idempotency_key = serializers.CharField(required=False, allow_blank=True)


class GuestSessionSerializer(serializers.ModelSerializer):
    """Serializer for GuestSession model."""
    
    class Meta:
        model = GuestSession
        fields = [
            'id', 'guest', 'token', 'device_id',
            'expires_at', 'is_active', 'created_at', 'last_used'
        ]
        read_only_fields = ['id', 'token', 'created_at', 'last_used']
