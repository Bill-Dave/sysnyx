"""
URL routing for payments module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, create_payment

router = DefaultRouter()
router.register(r'', PaymentViewSet, basename='payment')

urlpatterns = [
    path('create/', create_payment, name='create-payment'),
    path('', include(router.urls)),
]
