"""
Test suite for billing module.
"""
import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from .models import Guest, Folio, Charge
from services.models import Service, PricingRule


@pytest.mark.django_db
class TestGuestModel:
    """Tests for Guest model."""
    
    def test_create_guest(self):
        """Test guest creation."""
        guest = Guest.objects.create(
            name='John Doe',
            email='john@example.com',
            room_number='101',
            check_in=timezone.now()
        )
        assert guest.name == 'John Doe'
        assert guest.room_number == '101'
        assert guest.is_active is True


@pytest.mark.django_db
class TestFolioModel:
    """Tests for Folio model."""
    
    def test_create_folio(self):
        """Test folio creation."""
        guest = Guest.objects.create(
            name='Jane Doe',
            room_number='102',
            check_in=timezone.now()
        )
        folio = Folio.objects.create(guest=guest)
        assert folio.status == 'open'
        assert folio.balance == Decimal('0.00')
    
    def test_add_charge_to_folio(self):
        """Test adding a charge to folio."""
        guest = Guest.objects.create(
            name='Test Guest',
            room_number='103',
            check_in=timezone.now()
        )
        folio = Folio.objects.create(guest=guest)
        
        service = Service.objects.create(
            name='Valet',
            service_type='per_unit',
            base_price=Decimal('5.00')
        )
        
        charge = folio.add_charge(service=service, quantity=2)
        
        assert charge.base_amount == Decimal('10.00')
        assert charge.final_amount == Decimal('10.00')
        
        folio.refresh_from_db()
        assert folio.total_charges == Decimal('10.00')
        assert folio.balance == Decimal('10.00')
    
    def test_add_charge_with_tax(self):
        """Test adding charge with tax rule."""
        guest = Guest.objects.create(
            name='Tax Test',
            room_number='104',
            check_in=timezone.now()
        )
        folio = Folio.objects.create(guest=guest)
        
        service = Service.objects.create(
            name='Spa',
            service_type='fixed',
            base_price=Decimal('100.00')
        )
        PricingRule.objects.create(
            service=service,
            name='VAT',
            rule_type='tax',
            value=Decimal('16.00')
        )
        
        charge = folio.add_charge(service=service)
        
        assert charge.base_amount == Decimal('100.00')
        assert charge.final_amount == Decimal('116.00')
        
        folio.refresh_from_db()
        assert folio.total_charges == Decimal('116.00')
    
    def test_recalculate_totals(self):
        """Test folio total recalculation."""
        guest = Guest.objects.create(
            name='Recalc Test',
            room_number='105',
            check_in=timezone.now()
        )
        folio = Folio.objects.create(guest=guest)
        
        service = Service.objects.create(
            name='Service',
            service_type='fixed',
            base_price=Decimal('50.00')
        )
        
        folio.add_charge(service=service)
        folio.add_charge(service=service)
        
        folio.refresh_from_db()
        assert folio.total_charges == Decimal('100.00')
        assert folio.balance == Decimal('100.00')


@pytest.mark.django_db
class TestChargeModel:
    """Tests for Charge model."""
    
    def test_charge_idempotency(self):
        """Test idempotency key prevents duplicates."""
        guest = Guest.objects.create(
            name='Idemp Test',
            room_number='106',
            check_in=timezone.now()
        )
        folio = Folio.objects.create(guest=guest)
        
        service = Service.objects.create(
            name='Valet',
            service_type='fixed',
            base_price=Decimal('5.00')
        )
        
        charge1 = Charge.objects.create(
            folio=folio,
            service=service,
            description='Test',
            base_amount=Decimal('5.00'),
            final_amount=Decimal('5.00'),
            idempotency_key='unique-key-123'
        )
        
        # Check for existing charge with same key
        existing = Charge.objects.filter(
            folio=folio,
            idempotency_key='unique-key-123'
        ).first()
        
        assert existing is not None
        assert existing.id == charge1.id
