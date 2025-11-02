"""
Admin configuration for services module.
"""
from django.contrib import admin
from .models import Service, PricingRule


class PricingRuleInline(admin.TabularInline):
    model = PricingRule
    extra = 1
    fields = ['name', 'rule_type', 'value', 'priority', 'is_active']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'base_price', 'is_active', 'created_at']
    list_filter = ['service_type', 'is_active']
    search_fields = ['name', 'description']
    inlines = [PricingRuleInline]


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'service', 'rule_type', 'value', 'priority', 'is_active']
    list_filter = ['rule_type', 'is_active']
    search_fields = ['name', 'service__name']
