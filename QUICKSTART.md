# Sysnyx Quick Start Guide

## Prerequisites
- Python 3.10+ installed
- pip package manager
- Virtual environment (recommended)

## Installation Steps

### 1. Clone and Setup Environment
```bash
cd sysnyx
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env and set your configuration:
# - SECRET_KEY (generate a secure key)
# - STRIPE_SECRET_KEY (if using Stripe)
# - DATABASE_URL (optional, defaults to SQLite)
```

### 3. Initialize Database
```bash
python manage.py migrate
python manage.py createsuperuser  # Create admin account
python manage.py seed_services    # Load sample data
```

### 4. Run Development Server
```bash
python manage.py runserver
```

The application will be available at: http://127.0.0.1:8000/

## API Endpoints

### Authentication
- **POST** `/api/auth/token/` - Get authentication token
  ```json
  {
    "username": "admin",
    "password": "your_password"
  }
  ```

### Services
- **GET** `/api/services/` - List all services
- **POST** `/api/services/` - Create new service
- **GET** `/api/services/{id}/` - Get service details
- **PUT** `/api/services/{id}/` - Update service
- **DELETE** `/api/services/{id}/` - Delete service
- **POST** `/api/services/calc/preview/` - Preview charge calculation
  ```json
  {
    "service_id": 1,
    "quantity": 2,
    "extras": [{"name": "item", "price": 10.50}]
  }
  ```

### Billing
- **GET** `/api/billing/guests/` - List guests
- **POST** `/api/billing/guests/` - Create guest
- **GET** `/api/billing/folios/` - List folios
- **POST** `/api/billing/folios/{id}/add_charge/` - Add charge to folio
  ```json
  {
    "service_id": 1,
    "quantity": 2,
    "idempotency_key": "unique-key-123"
  }
  ```
- **POST** `/api/billing/charge/{room_number}/` - Add charge by room (NFC endpoint)

### Payments
- **GET** `/api/payments/` - List payments
- **POST** `/api/payments/create/` - Create and process payment
  ```json
  {
    "folio_id": 1,
    "amount": 100.00,
    "payment_method": "cash"
  }
  ```

## Admin Interface
Access the Django admin at: http://127.0.0.1:8000/admin/

## Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Module
```bash
pytest services/tests.py -v
pytest billing/tests.py -v
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

## Sample Data
After running `seed_services`, you'll have:
- 5 services (Valet, Spa, Restaurant, Room Service, Laundry)
- 8 pricing rules (taxes, discounts, surcharges)
- 3 sample guests in rooms 101, 205, and 310

## API Authentication
All API endpoints require authentication. Include the token in your requests:
```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" http://localhost:8000/api/services/
```

## Common Tasks

### Add a New Service
```bash
curl -X POST http://localhost:8000/api/services/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pool Access",
    "service_type": "fixed",
    "base_price": "15.00",
    "description": "Daily pool access"
  }'
```

### Calculate Charge Preview
```bash
curl -X POST http://localhost:8000/api/services/calc/preview/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": 1,
    "quantity": 3
  }'
```

### Add Charge to Guest Folio
```bash
curl -X POST http://localhost:8000/api/billing/charge/101/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": 1,
    "quantity": 2,
    "idempotency_key": "nfc-tap-uuid-123"
  }'
```

## Troubleshooting

### Database Issues
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py seed_services
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use
```bash
# Use different port
python manage.py runserver 8080
```

## Next Steps
1. Configure Stripe for payment processing
2. Set up Celery for async tasks
3. Configure Redis for caching
4. Deploy to production (AWS/Heroku)
5. Integrate with hotel PMS system
6. Add frontend dashboard (React)
7. Build SysPay mobile app (React Native)

## Support
For issues and questions, refer to the main README.md or create an issue in the repository.
