"""
Billing models for guests, folios, and charges.
"""
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from services.models import Service


class Guest(models.Model):
    """
    Hotel guest information.
    """
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    room_number = models.CharField(max_length=20)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['room_number']
        indexes = [
            models.Index(fields=['room_number']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.name} - Room {self.room_number}"


class Folio(models.Model):
    """
    Guest billing folio aggregating all charges and payments.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('settled', 'Settled'),
        ('cancelled', 'Cancelled'),
    ]
    
    guest = models.OneToOneField(
        Guest,
        on_delete=models.CASCADE,
        related_name='folio'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    total_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_payments = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Folio for {self.guest.name} - {self.status}"
    
    def recalculate_totals(self):
        """
        Recalculate folio totals from charges and payments.
        """
        from django.db.models import Sum
        
        charges_sum = self.charges.aggregate(
            total=Sum('final_amount')
        )['total'] or Decimal('0.00')
        
        payments_sum = self.payments.filter(
            status='completed'
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        self.total_charges = charges_sum
        self.total_payments = payments_sum
        self.balance = charges_sum - payments_sum
        self.save()
    
    def add_charge(self, service, quantity=1, extras=None, description=''):
        """
        Add a charge to this folio.
        
        Args:
            service: Service instance
            quantity: Quantity for per_unit services
            extras: Menu items for variable services
            description: Optional charge description
        
        Returns:
            Charge: Created charge instance
        """
        base_amount = service.calculate_amount(quantity=quantity, extras=extras)
        final_amount, breakdown = service.apply_rules(base_amount)
        
        charge = Charge.objects.create(
            folio=self,
            service=service,
            description=description or service.name,
            quantity=quantity,
            base_amount=base_amount,
            final_amount=final_amount,
            breakdown=breakdown
        )
        
        self.recalculate_totals()
        return charge


class Charge(models.Model):
    """
    Individual charge on a folio.
    """
    folio = models.ForeignKey(
        Folio,
        on_delete=models.CASCADE,
        related_name='charges'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='charges'
    )
    description = models.CharField(max_length=500)
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    breakdown = models.JSONField(default=list)
    idempotency_key = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text='Prevents duplicate charges from NFC taps'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['folio', '-created_at']),
            models.Index(fields=['idempotency_key']),
        ]
    
    def __str__(self):
        return f"{self.description} - ${self.final_amount}"


class GuestSession(models.Model):
    """
    Ephemeral session tokens for SysPay app authentication.
    """
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    token = models.CharField(max_length=64, unique=True, db_index=True)
    device_id = models.CharField(max_length=100, blank=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session for {self.guest.name} - {self.token[:8]}..."
    
    def is_valid(self):
        """Check if session is still valid."""
        from django.utils import timezone
        return self.is_active and self.expires_at > timezone.now()
