"""
URL routing for billing module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GuestViewSet, FolioViewSet, charge_by_room

router = DefaultRouter()
router.register(r'guests', GuestViewSet, basename='guest')
router.register(r'folios', FolioViewSet, basename='folio')

urlpatterns = [
    path('charge/<str:room_number>/', charge_by_room, name='charge-by-room'),
    path('', include(router.urls)),
]
