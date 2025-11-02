"""
API views for services module.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from .models import Service, PricingRule
from .serializers import (
    ServiceSerializer,
    PricingRuleSerializer,
    ChargePreviewSerializer
)


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Service CRUD operations.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter active services by default."""
        queryset = super().get_queryset()
        if self.request.query_params.get('include_inactive') != 'true':
            queryset = queryset.filter(is_active=True)
        return queryset


class PricingRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PricingRule CRUD operations.
    """
    queryset = PricingRule.objects.all()
    serializer_class = PricingRuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by service if provided."""
        queryset = super().get_queryset()
        service_id = self.request.query_params.get('service_id')
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        return queryset


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def preview_calc(request):
    """
    Preview charge calculation for a service.
    
    POST /api/services/calc/preview/
    Body: {
        "service_id": 1,
        "quantity": 2,
        "extras": [{"name": "item1", "price": 10.50}]  # Optional
    }
    
    Returns: {
        "base": "20.00",
        "final": "23.20",
        "breakdown": [...]
    }
    """
    serializer = ChargePreviewSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    data = serializer.validated_data
    
    try:
        service = Service.objects.get(id=data['service_id'])
        
        # Calculate base amount
        base_amount = service.calculate_amount(
            quantity=data.get('quantity', 1),
            extras=data.get('extras')
        )
        
        # Apply pricing rules
        final_amount, breakdown = service.apply_rules(base_amount)
        
        return Response({
            'service_id': service.id,
            'service_name': service.name,
            'base': str(base_amount),
            'final': str(final_amount),
            'breakdown': breakdown
        }, status=status.HTTP_200_OK)
    
    except Service.DoesNotExist:
        return Response(
            {'error': 'Service not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValidationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    except Exception as e:
        return Response(
            {'error': f'Calculation error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
