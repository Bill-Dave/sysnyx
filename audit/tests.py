"""
Test suite for audit module.
"""
import pytest
from .models import AuditLog, log_action


@pytest.mark.django_db
class TestAuditLog:
    """Tests for AuditLog model."""
    
    def test_create_audit_log(self):
        """Test audit log creation."""
        log = log_action(
            action_type='charge_created',
            entity_type='Charge',
            entity_id=1,
            actor_name='staff@hotel.com',
            new_values={'amount': '50.00'}
        )
        
        assert log.action_type == 'charge_created'
        assert log.entity_type == 'Charge'
        assert log.entity_id == 1
    
    def test_audit_log_immutable(self):
        """Test that audit logs cannot be modified."""
        log = log_action(
            action_type='payment_created',
            entity_type='Payment',
            entity_id=1,
            actor_name='system'
        )
        
        log.actor_name = 'hacker'
        
        with pytest.raises(ValueError, match='immutable'):
            log.save()
    
    def test_audit_log_cannot_delete(self):
        """Test that audit logs cannot be deleted."""
        log = log_action(
            action_type='folio_settled',
            entity_type='Folio',
            entity_id=1,
            actor_name='system'
        )
        
        with pytest.raises(ValueError, match='cannot be deleted'):
            log.delete()
