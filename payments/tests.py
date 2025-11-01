"""
Test suite for payments module.
"""
import pytest
from decimal import Decimal
from django.utils import timezone
from .models import Payment
from billing.models import Guest, Folio


@pytest.mark.django_db
class TestPaymentModel:
    """Tests for Payment model."""
    
    def test_create_payment(self):
        """Test payment creation."""
        guest = Guest.objects.create(
            name='Payment Test',
            room_number='201',
            check_in=timezone.now()
        )
        folio = Folio.objects.create(guest=guest)
        
        payment = Payment.objects.create(
            folio=folio,
            amount=Decimal('100.00'),
            payment_method='stripe'
        )
        
        assert payment.status == 'pending'
        assert payment.amount == Decimal('100.00')
    
    def test_process_cash_payment(self):
        """Test processing cash payment."""
        guest = Guest.objects.create(
            name='Cash Test',
            room_number='202',
            check_in=timezone.now()
        )
        folio = Folio.objects.create(guest=guest)
        
        payment = Payment.objects.create(
            folio=folio,
            amount=Decimal('50.00'),
            payment_method='cash'
        )
        
        status = payment.process_payment()
        
        assert status == 'completed'
        assert payment.completed_at is not None
