"""
Payment processing models.
"""
from decimal import Decimal
from django.db import models
from billing.models import Folio


class Payment(models.Model):
    """
    Payment transaction record.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('stripe', 'Stripe'),
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash'),
        ('card', 'Card'),
    ]
    
    folio = models.ForeignKey(
        Folio,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Stripe/external payment details
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    stripe_token = models.CharField(max_length=200, blank=True)
    mpesa_transaction_id = models.CharField(max_length=200, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['folio', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]
    
    def __str__(self):
        return f"Payment {self.id} - {self.payment_method} - ${self.amount} ({self.status})"
    
    def process_payment(self):
        """
        Process payment based on payment method.
        This is a stub - actual implementation would integrate with Stripe/M-Pesa.
        """
        from django.utils import timezone
        
        if self.payment_method == 'stripe':
            # Stripe integration would go here
            # stripe.PaymentIntent.create(...)
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()
            
            # Update folio
            self.folio.recalculate_totals()
            
        elif self.payment_method == 'mpesa':
            # M-Pesa integration would go here
            self.status = 'processing'
            self.save()
            
        elif self.payment_method in ['cash', 'card']:
            # Manual payment methods
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()
            
            # Update folio
            self.folio.recalculate_totals()
        
        return self.status
