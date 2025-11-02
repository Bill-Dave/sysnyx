"""
DRF serializers for services module.
"""
from rest_framework import serializers
from .models import Service, PricingRule


class PricingRuleSerializer(serializers.ModelSerializer):
    """
    Serializer for PricingRule model.
    """
    class Meta:
        model = PricingRule
        fields = [
            'id', 'name', 'rule_type', 'value', 'conditions',
            'priority', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Service model with nested pricing rules.
    """
    pricing_rules = PricingRuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 'service_type', 'base_price',
            'is_active', 'pricing_rules', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_base_price(self, value):
        """Ensure base price is positive."""
        if value < 0:
            raise serializers.ValidationError('Base price must be non-negative.')
        return value


class ChargePreviewSerializer(serializers.Serializer):
    """
    Serializer for charge preview calculations.
    """
    service_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)
    extras = serializers.JSONField(required=False, allow_null=True)
    
    def validate_service_id(self, value):
        """Ensure service exists and is active."""
        try:
            service = Service.objects.get(id=value)
            if not service.is_active:
                raise serializers.ValidationError('Service is not active.')
        except Service.DoesNotExist:
            raise serializers.ValidationError('Service not found.')
        return value
