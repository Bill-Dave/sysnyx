"""
Test suite for services module.
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Service, PricingRule


@pytest.mark.django_db
class TestServiceModel:
    """Tests for Service model."""
    
    def test_fixed_price_calculation(self):
        """Test fixed price service calculation."""
        service = Service.objects.create(
            name='Room Cleaning',
            service_type='fixed',
            base_price=Decimal('50.00')
        )
        assert service.calculate_amount() == Decimal('50.00')
        assert service.calculate_amount(quantity=5) == Decimal('50.00')
    
    def test_per_unit_calculation(self):
        """Test per-unit service calculation."""
        service = Service.objects.create(
            name='Valet Parking',
            service_type='per_unit',
            base_price=Decimal('5.00')
        )
        assert service.calculate_amount(quantity=1) == Decimal('5.00')
        assert service.calculate_amount(quantity=3) == Decimal('15.00')
    
    def test_per_unit_invalid_quantity(self):
        """Test per-unit with invalid quantity."""
        service = Service.objects.create(
            name='Valet',
            service_type='per_unit',
            base_price=Decimal('5.00')
        )
        with pytest.raises(ValidationError, match='Quantity must be positive'):
            service.calculate_amount(quantity=0)
    
    def test_variable_calculation(self):
        """Test variable price calculation with menu items."""
        service = Service.objects.create(
            name='Restaurant',
            service_type='variable',
            base_price=Decimal('0.00')
        )
        extras = [
            {'name': 'Steak', 'price': 25.50},
            {'name': 'Wine', 'price': 15.00}
        ]
        assert service.calculate_amount(extras=extras) == Decimal('40.50')
    
    def test_variable_with_json_string(self):
        """Test variable calculation with JSON string input."""
        service = Service.objects.create(
            name='Restaurant',
            service_type='variable',
            base_price=Decimal('0.00')
        )
        extras_json = '[{"name": "Coffee", "price": 5.00}]'
        assert service.calculate_amount(extras=extras_json) == Decimal('5.00')
    
    def test_variable_invalid_extras(self):
        """Test variable with invalid extras format."""
        service = Service.objects.create(
            name='Restaurant',
            service_type='variable',
            base_price=Decimal('0.00')
        )
        with pytest.raises(ValidationError, match='Invalid JSON format'):
            service.calculate_amount(extras="not a list")


@pytest.mark.django_db
class TestPricingRule:
    """Tests for PricingRule model."""
    
    def test_tax_rule(self):
        """Test tax rule application."""
        service = Service.objects.create(
            name='Spa',
            service_type='fixed',
            base_price=Decimal('100.00')
        )
        rule = PricingRule.objects.create(
            service=service,
            name='VAT',
            rule_type='tax',
            value=Decimal('16.00')
        )
        result = rule.apply_to_amount(Decimal('100.00'))
        assert result == Decimal('116.00')
    
    def test_discount_rule(self):
        """Test discount rule application."""
        service = Service.objects.create(
            name='Spa',
            service_type='fixed',
            base_price=Decimal('100.00')
        )
        rule = PricingRule.objects.create(
            service=service,
            name='Member Discount',
            rule_type='discount',
            value=Decimal('10.00')
        )
        result = rule.apply_to_amount(Decimal('100.00'))
        assert result == Decimal('90.00')
    
    def test_peak_hours_condition(self):
        """Test peak hours condition."""
        service = Service.objects.create(
            name='Dining',
            service_type='fixed',
            base_price=Decimal('50.00')
        )
        rule = PricingRule.objects.create(
            service=service,
            name='Peak Surcharge',
            rule_type='surcharge',
            value=Decimal('20.00'),
            conditions={'peak_hours': '18:00-22:00'}
        )
        
        # During peak hours
        peak_time = timezone.datetime.strptime('19:30', '%H:%M').time()
        context = {'time': timezone.datetime.combine(timezone.now().date(), peak_time)}
        result = rule.apply_to_amount(Decimal('50.00'), context)
        assert result == Decimal('60.00')
    
    def test_apply_multiple_rules(self):
        """Test applying multiple rules in order."""
        service = Service.objects.create(
            name='Spa',
            service_type='fixed',
            base_price=Decimal('100.00')
        )
        PricingRule.objects.create(
            service=service,
            name='Discount',
            rule_type='discount',
            value=Decimal('10.00'),
            priority=1
        )
        PricingRule.objects.create(
            service=service,
            name='VAT',
            rule_type='tax',
            value=Decimal('16.00'),
            priority=2
        )
        
        base = service.calculate_amount()
        final, breakdown = service.apply_rules(base)
        
        # 100 - 10% = 90, then 90 + 16% = 104.40
        assert final == Decimal('104.40')
        assert len(breakdown) == 4  # base, discount, tax, final
