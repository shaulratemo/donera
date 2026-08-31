import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from organizations.models import Organization

User = get_user_model()

# Create an org user
email = 'test_org@example.com'
pwd = 'TestPass123!'
User.objects.filter(email=email).delete()
org_user = User.objects.create_user(
    email=email, 
    password=pwd, 
    role='ORGANIZATION',
    first_name='Test',
    last_name='Org'
)

# Create an organization
Organization.objects.filter(owner=org_user).delete()
org = Organization.objects.create(
    owner=org_user,
    name='Test Org',
    description='Test',
    registration_number='REG123',
    kra_pin='KRA123',
    tcc_number='TCC123',
    verification_status='APPROVED'
)

# Try creating a cause
client = APIClient()
token_response = client.post('/api/users/login/', {'email': email, 'password': pwd}, format='json')
print('Login Response Status:', token_response.status_code)
access_token = token_response.data.get('access') if hasattr(token_response, 'data') else None
print('Access Token Obtained:', bool(access_token))

if access_token:
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

payload = {
    'title': 'Test Cause',
    'description': 'Test Description',
    'category': 'Health',
    'status': 'ACTIVE',
    'target_amount': '5000.00'
}

response = client.post('/api/causes/create/', payload, format='json')
print('Create Cause Status Code:', response.status_code)
print('Response Data:', response.data if hasattr(response, 'data') else response.content)

# Cleanup
User.objects.filter(email=email).delete()
