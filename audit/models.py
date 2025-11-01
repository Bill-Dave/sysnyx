"""
Audit logging models for immutable transaction tracking.
"""
from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):
    """
    Immutable audit trail for all billing and payment operations.
    """
    ACTION_TYPES = [
        ('charge_created', 'Charge Created'),
        ('charge_modified', 'Charge Modified'),
        ('payment_created', 'Payment Created'),
        ('payment_processed', 'Payment Processed'),
        ('payment_failed', 'Payment Failed'),
        ('folio_settled', 'Folio Settled'),
        ('folio_cancelled', 'Folio Cancelled'),
    ]
    
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    entity_type = models.CharField(max_length=50, help_text='Model name (e.g., Charge, Payment)')
    entity_id = models.IntegerField(help_text='ID of the affected entity')
    
    # Actor information
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    actor_name = models.CharField(max_length=200, help_text='Name of actor (user/system)')
    
    # Change details
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Request context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    
    # Timestamp (immutable)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['action_type']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.action_type} - {self.entity_type}:{self.entity_id} by {self.actor_name}"
    
    def save(self, *args, **kwargs):
        """Override save to prevent updates after creation."""
        if self.pk is not None:
            raise ValueError('AuditLog entries are immutable and cannot be updated.')
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of audit logs."""
        raise ValueError('AuditLog entries cannot be deleted.')


def log_action(action_type, entity_type, entity_id, actor_name, old_values=None, new_values=None, metadata=None, user=None, ip_address=None, user_agent=None):
    """
    Helper function to create audit log entries.
    
    Args:
        action_type: Type of action performed
        entity_type: Model name of affected entity
        entity_id: ID of affected entity
        actor_name: Name of actor performing action
        old_values: Previous state (for modifications)
        new_values: New state
        metadata: Additional context
        user: Django User instance
        ip_address: IP address of request
        user_agent: User agent string
    
    Returns:
        AuditLog: Created audit log entry
    """
    return AuditLog.objects.create(
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_name=actor_name,
        old_values=old_values or {},
        new_values=new_values or {},
        metadata=metadata or {},
        user=user,
        ip_address=ip_address,
        user_agent=user_agent or ''
    )
