"""
Service catalog models with pricing logic.
"""
import json
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Service(models.Model):
    """
    Service catalog entry with flexible pricing.
    """
    SERVICE_TYPES = [
        ('fixed', 'Fixed Price'),
        ('per_unit', 'Per Unit'),
        ('variable', 'Variable (Menu Items)'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()})"
    
    def calculate_amount(self, quantity=1, extras=None):
        """
        Calculate service amount based on type.
        
        Args:
            quantity: Number of units (for per_unit type)
            extras: List of menu items with prices (for variable type)
        
        Returns:
            Decimal: Calculated amount
        """
        if self.service_type == 'fixed':
            amount = self.base_price
        elif self.service_type == 'per_unit':
            if quantity <= 0:
                raise ValidationError('Quantity must be positive for per_unit services.')
            amount = self.base_price * Decimal(quantity)
        elif self.service_type == 'variable':
            if isinstance(extras, str):
                try:
                    extras = json.loads(extras)
                except json.JSONDecodeError:
                    raise ValidationError('Invalid JSON format for extras.')
            
            if not isinstance(extras, list):
                raise ValidationError('Extras must be a list of items.')
            
            amount = Decimal('0.00')
            for item in extras:
                if not isinstance(item, dict):
                    raise ValidationError('Each extra item must be a dictionary.')
                amount += Decimal(str(item.get('price', 0)))
        else:
            raise ValidationError(f'Unknown service type: {self.service_type}')
        
        return amount.quantize(Decimal('0.01'))
    
    def apply_rules(self, base_amount, context=None):
        """
        Apply all active pricing rules to base amount.
        
        Args:
            base_amount: Base calculated amount
            context: Optional context dict (e.g., {'time': datetime.now()})
        
        Returns:
            tuple: (final_amount, breakdown_list)
        """
        breakdown = [{'type': 'base', 'amount': str(base_amount)}]
        final_amount = base_amount
        
        rules = self.pricing_rules.filter(is_active=True).order_by('priority')
        for rule in rules:
            rule_amount = rule.apply_to_amount(final_amount, context)
            if rule_amount != final_amount:
                breakdown.append({
                    'type': rule.rule_type,
                    'name': rule.name,
                    'amount': str(rule_amount - final_amount)
                })
                final_amount = rule_amount
        
        breakdown.append({'type': 'final', 'amount': str(final_amount)})
        return final_amount, breakdown


class PricingRule(models.Model):
    """
    Pricing rules for taxes, discounts, surcharges.
    """
    RULE_TYPES = [
        ('tax', 'Tax'),
        ('discount', 'Discount'),
        ('surcharge', 'Surcharge'),
    ]
    
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='pricing_rules'
    )
    name = models.CharField(max_length=200)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Percentage value (e.g., 16.00 for 16%)'
    )
    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text='Optional conditions (e.g., {"peak_hours": "18:00-22:00"})'
    )
    priority = models.IntegerField(default=0, help_text='Lower values apply first')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['priority', 'created_at']
    
    def __str__(self):
        return f"{self.name} ({self.value}%) on {self.service.name}"
    
    def apply_to_amount(self, base_amount, context=None):
        """
        Apply this rule to an amount.
        
        Args:
            base_amount: Amount to apply rule to
            context: Optional context for condition checking
        
        Returns:
            Decimal: Modified amount
        """
        # Check conditions
        if self.conditions.get('peak_hours'):
            now = context.get('time', timezone.now()).time() if context else timezone.now().time()
            try:
                start_str, end_str = self.conditions['peak_hours'].split('-')
                start_time = timezone.datetime.strptime(start_str.strip(), '%H:%M').time()
                end_time = timezone.datetime.strptime(end_str.strip(), '%H:%M').time()
                
                if not (start_time <= now <= end_time):
                    return base_amount
            except (ValueError, AttributeError):
                pass
        
        # Apply rule
        if self.rule_type in ['tax', 'surcharge']:
            factor = Decimal('1') + (self.value / Decimal('100'))
        else:  # discount
            factor = Decimal('1') - (self.value / Decimal('100'))
        
        result = (base_amount * factor).quantize(Decimal('0.01'))
        return result
