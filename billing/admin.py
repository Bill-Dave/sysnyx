"""
Admin configuration for billing module.
"""
from django.contrib import admin
from .models import Guest, Folio, Charge, GuestSession


class FolioInline(admin.StackedInline):
    model = Folio
    extra = 0
    readonly_fields = ['total_charges', 'total_payments', 'balance']


class ChargeInline(admin.TabularInline):
    model = Charge
    extra = 0
    readonly_fields = ['base_amount', 'final_amount', 'created_at']


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['name', 'room_number', 'email', 'check_in', 'is_active']
    list_filter = ['is_active', 'check_in']
    search_fields = ['name', 'email', 'room_number']
    inlines = [FolioInline]


@admin.register(Folio)
class FolioAdmin(admin.ModelAdmin):
    list_display = ['guest', 'status', 'total_charges', 'balance', 'created_at']
    list_filter = ['status']
    search_fields = ['guest__name', 'guest__room_number']
    readonly_fields = ['total_charges', 'total_payments', 'balance']
    inlines = [ChargeInline]


@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = ['description', 'folio', 'final_amount', 'created_at']
    list_filter = ['created_at', 'service']
    search_fields = ['description', 'folio__guest__name']
    readonly_fields = ['base_amount', 'final_amount', 'breakdown', 'created_at']


@admin.register(GuestSession)
class GuestSessionAdmin(admin.ModelAdmin):
    list_display = ['guest', 'token', 'is_active', 'expires_at', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['guest__name', 'token']
    readonly_fields = ['token', 'created_at', 'last_used']
