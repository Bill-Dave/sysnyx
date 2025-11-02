"""
URL routing for services module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, PricingRuleViewSet, preview_calc

router = DefaultRouter()
router.register(r'', ServiceViewSet, basename='service')
router.register(r'rules', PricingRuleViewSet, basename='pricing-rule')

urlpatterns = [
    path('calc/preview/', preview_calc, name='preview-calc'),
    path('', include(router.urls)),
]
