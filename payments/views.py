"""
API views for payments module.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from billing.models import Folio
from .models import Payment
from .serializers import PaymentSerializer, CreatePaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment operations."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by folio if provided."""
        queryset = super().get_queryset()
        folio_id = self.request.query_params.get('folio_id')
        if folio_id:
            queryset = queryset.filter(folio_id=folio_id)
        return queryset
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process a pending payment."""
        payment = self.get_object()
        
        if payment.status != 'pending':
            return Response(
                {'error': f'Payment is already {payment.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            payment.process_payment()
            serializer = self.get_serializer(payment)
            return Response(serializer.data)
        except Exception as e:
            payment.status = 'failed'
            payment.error_message = str(e)
            payment.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    """
    Create and process a payment.
    
    POST /api/payments/create/
    Body: {
        "folio_id": 1,
        "amount": 100.00,
        "payment_method": "stripe",
        "stripe_token": "tok_xxx",
        "metadata": {}
    }
    """
    serializer = CreatePaymentSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    data = serializer.validated_data
    
    try:
        folio = get_object_or_404(Folio, id=data['folio_id'])
        
        payment = Payment.objects.create(
            folio=folio,
            amount=data['amount'],
            payment_method=data['payment_method'],
            stripe_token=data.get('stripe_token', ''),
            metadata=data.get('metadata', {})
        )
        
        # Process payment immediately
        payment.process_payment()
        
        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
