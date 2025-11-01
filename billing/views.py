"""
API views for billing module.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from services.models import Service
from .models import Guest, Folio, Charge, GuestSession
from .serializers import (
    GuestSerializer,
    FolioSerializer,
    ChargeSerializer,
    AddChargeSerializer,
    GuestSessionSerializer
)


class GuestViewSet(viewsets.ModelViewSet):
    """ViewSet for Guest CRUD operations."""
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter active guests by default."""
        queryset = super().get_queryset()
        if self.request.query_params.get('include_inactive') != 'true':
            queryset = queryset.filter(is_active=True)
        return queryset
    
    @action(detail=True, methods=['get'])
    def folio(self, request, pk=None):
        """Get guest's folio."""
        guest = self.get_object()
        try:
            folio = guest.folio
            serializer = FolioSerializer(folio)
            return Response(serializer.data)
        except Folio.DoesNotExist:
            return Response(
                {'error': 'Folio not found for this guest.'},
                status=status.HTTP_404_NOT_FOUND
            )


class FolioViewSet(viewsets.ModelViewSet):
    """ViewSet for Folio operations."""
    queryset = Folio.objects.all()
    serializer_class = FolioSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def add_charge(self, request, pk=None):
        """
        Add a charge to the folio.
        
        POST /api/billing/folios/{id}/add_charge/
        Body: {
            "service_id": 1,
            "quantity": 2,
            "extras": [...],
            "description": "Optional",
            "idempotency_key": "unique-key"
        }
        """
        folio = self.get_object()
        serializer = AddChargeSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        data = serializer.validated_data
        
        # Check idempotency
        idempotency_key = data.get('idempotency_key', '')
        if idempotency_key:
            existing = Charge.objects.filter(
                folio=folio,
                idempotency_key=idempotency_key
            ).first()
            if existing:
                return Response(
                    ChargeSerializer(existing).data,
                    status=status.HTTP_200_OK
                )
        
        try:
            service = Service.objects.get(id=data['service_id'], is_active=True)
            
            charge = folio.add_charge(
                service=service,
                quantity=data.get('quantity', 1),
                extras=data.get('extras'),
                description=data.get('description', '')
            )
            
            if idempotency_key:
                charge.idempotency_key = idempotency_key
                charge.save()
            
            return Response(
                ChargeSerializer(charge).data,
                status=status.HTTP_201_CREATED
            )
        
        except Service.DoesNotExist:
            return Response(
                {'error': 'Service not found or inactive.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate folio totals."""
        folio = self.get_object()
        folio.recalculate_totals()
        serializer = self.get_serializer(folio)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def charge_by_room(request, room_number):
    """
    Add charge by room number (NFC tap endpoint).
    
    POST /api/billing/charge/{room_number}/
    Body: {
        "service_id": 1,
        "quantity": 2,
        "idempotency_key": "nfc-tap-uuid"
    }
    """
    try:
        guest = Guest.objects.get(room_number=room_number, is_active=True)
        folio, created = Folio.objects.get_or_create(
            guest=guest,
            defaults={'status': 'open'}
        )
        
        serializer = AddChargeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        data = serializer.validated_data
        
        # Check idempotency
        idempotency_key = data.get('idempotency_key', '')
        if idempotency_key:
            existing = Charge.objects.filter(
                folio=folio,
                idempotency_key=idempotency_key
            ).first()
            if existing:
                return Response(
                    ChargeSerializer(existing).data,
                    status=status.HTTP_200_OK
                )
        
        service = get_object_or_404(Service, id=data['service_id'], is_active=True)
        
        charge = folio.add_charge(
            service=service,
            quantity=data.get('quantity', 1),
            extras=data.get('extras'),
            description=data.get('description', '')
        )
        
        if idempotency_key:
            charge.idempotency_key = idempotency_key
            charge.save()
        
        return Response(
            ChargeSerializer(charge).data,
            status=status.HTTP_201_CREATED
        )
    
    except Guest.DoesNotExist:
        return Response(
            {'error': f'No active guest found in room {room_number}.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
