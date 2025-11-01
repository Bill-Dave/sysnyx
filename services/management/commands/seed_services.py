"""
Management command to seed sample services and pricing rules.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from services.models import Service, PricingRule
from billing.models import Guest, Folio


class Command(BaseCommand):
    help = 'Seeds the database with sample services, pricing rules, and test guests'
    
    def handle(self, *args, **options):
        self.stdout.write('Seeding services...')
        
        # Clear existing data
        Service.objects.all().delete()
        
        # Create services
        valet = Service.objects.create(
            name='Valet Parking',
            description='Professional valet parking service',
            service_type='per_unit',
            base_price=Decimal('5.00')
        )
        self.stdout.write(self.style.SUCCESS(f'Created: {valet.name}'))
        
        # Add VAT to valet
        PricingRule.objects.create(
            service=valet,
            name='VAT 16%',
            rule_type='tax',
            value=Decimal('16.00'),
            priority=1
        )
        
        spa = Service.objects.create(
            name='Spa Treatment',
            description='Luxury spa and massage services',
            service_type='fixed',
            base_price=Decimal('100.00')
        )
        self.stdout.write(self.style.SUCCESS(f'Created: {spa.name}'))
        
        # Add VAT and member discount to spa
        PricingRule.objects.create(
            service=spa,
            name='Member Discount',
            rule_type='discount',
            value=Decimal('10.00'),
            priority=1
        )
        PricingRule.objects.create(
            service=spa,
            name='VAT 16%',
            rule_type='tax',
            value=Decimal('16.00'),
            priority=2
        )
        
        restaurant = Service.objects.create(
            name='Restaurant Dining',
            description='Fine dining restaurant',
            service_type='variable',
            base_price=Decimal('0.00')
        )
        self.stdout.write(self.style.SUCCESS(f'Created: {restaurant.name}'))
        
        # Add service charge and VAT to restaurant
        PricingRule.objects.create(
            service=restaurant,
            name='Service Charge',
            rule_type='surcharge',
            value=Decimal('10.00'),
            priority=1
        )
        PricingRule.objects.create(
            service=restaurant,
            name='VAT 16%',
            rule_type='tax',
            value=Decimal('16.00'),
            priority=2
        )
        
        room_service = Service.objects.create(
            name='Room Service',
            description='24/7 in-room dining',
            service_type='variable',
            base_price=Decimal('0.00')
        )
        self.stdout.write(self.style.SUCCESS(f'Created: {room_service.name}'))
        
        # Add peak hours surcharge to room service
        PricingRule.objects.create(
            service=room_service,
            name='Peak Hours Surcharge',
            rule_type='surcharge',
            value=Decimal('20.00'),
            conditions={'peak_hours': '18:00-22:00'},
            priority=1
        )
        PricingRule.objects.create(
            service=room_service,
            name='VAT 16%',
            rule_type='tax',
            value=Decimal('16.00'),
            priority=2
        )
        
        laundry = Service.objects.create(
            name='Laundry Service',
            description='Same-day laundry and dry cleaning',
            service_type='per_unit',
            base_price=Decimal('8.00')
        )
        self.stdout.write(self.style.SUCCESS(f'Created: {laundry.name}'))
        
        PricingRule.objects.create(
            service=laundry,
            name='VAT 16%',
            rule_type='tax',
            value=Decimal('16.00'),
            priority=1
        )
        
        # Create sample guests
        self.stdout.write('\nSeeding sample guests...')
        
        guest1 = Guest.objects.create(
            name='John Doe',
            email='john.doe@example.com',
            phone='+254712345678',
            room_number='101',
            check_in=timezone.now()
        )
        Folio.objects.create(guest=guest1)
        self.stdout.write(self.style.SUCCESS(f'Created guest: {guest1.name} - Room {guest1.room_number}'))
        
        guest2 = Guest.objects.create(
            name='Jane Smith',
            email='jane.smith@example.com',
            phone='+254723456789',
            room_number='205',
            check_in=timezone.now()
        )
        Folio.objects.create(guest=guest2)
        self.stdout.write(self.style.SUCCESS(f'Created guest: {guest2.name} - Room {guest2.room_number}'))
        
        guest3 = Guest.objects.create(
            name='Alice Johnson',
            email='alice.j@example.com',
            phone='+254734567890',
            room_number='310',
            check_in=timezone.now()
        )
        Folio.objects.create(guest=guest3)
        self.stdout.write(self.style.SUCCESS(f'Created guest: {guest3.name} - Room {guest3.room_number}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Database seeded successfully!'))
        self.stdout.write(f'Total services: {Service.objects.count()}')
        self.stdout.write(f'Total pricing rules: {PricingRule.objects.count()}')
        self.stdout.write(f'Total guests: {Guest.objects.count()}')
