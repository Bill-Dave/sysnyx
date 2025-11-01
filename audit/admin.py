"""
Admin configuration for audit module.
"""
from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        'action_type', 'entity_type', 'entity_id',
        'actor_name', 'created_at'
    ]
    list_filter = ['action_type', 'entity_type', 'created_at']
    search_fields = ['actor_name', 'entity_type', 'entity_id']
    readonly_fields = [
        'action_type', 'entity_type', 'entity_id', 'user',
        'actor_name', 'old_values', 'new_values', 'metadata',
        'ip_address', 'user_agent', 'created_at'
    ]
    
    def has_add_permission(self, request):
        """Prevent manual creation of audit logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit logs."""
        return False
