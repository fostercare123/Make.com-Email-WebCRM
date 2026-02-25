#!/usr/bin/env python3
"""
Discover available endpoints in webCRM
"""
import requests
from dotenv import load_dotenv
import os

load_dotenv(override=True)
auth_code = os.getenv('WEBCRM_TOKEN').strip()
base_url = os.getenv('WEBCRM_BASE_URL').strip()

print('🔍 Discovering webCRM API endpoints...\n')

# Get Access Token
auth_response = requests.post(f'{base_url}/Auth/ApiLogin', data={'authCode': auth_code}, timeout=10)
access_token = auth_response.json().get('AccessToken')

headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json'
}

# List of common endpoints to test
endpoints = [
    '/Organisations',
    '/Persons',
    '/Opportunities',
    '/Products',
    '/Quotations',
    '/Deliveries',
    '/Invoices',
    '/Tasks',
    '/Activities',
    '/Notes',
    '/Files',
    '/RelationshipTypes',
    '/Tags',
    '/CustomFields',
]

print('Testing endpoints:\n')
print('=' * 70)

available_endpoints = []

for endpoint in endpoints:
    try:
        response = requests.get(f'{base_url}{endpoint}?page=1&size=1', headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 'object'
            available_endpoints.append(endpoint)
            print(f'✅ {endpoint:25} - Available')
        elif response.status_code == 404:
            print(f'❌ {endpoint:25} - Not Found (404)')
        else:
            print(f'⚠️  {endpoint:25} - Status {response.status_code}')
    except Exception as e:
        print(f'❌ {endpoint:25} - Error')

print('\n' + '=' * 70)
print(f'\nAvailable endpoints: {len(available_endpoints)}')
for ep in available_endpoints:
    print(f'  - {ep}')

print('\n💡 Which endpoint should we use for updating item prices?')
