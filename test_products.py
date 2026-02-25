#!/usr/bin/env python3
"""
Test to find the correct Products endpoint in webCRM
"""
import requests
from dotenv import load_dotenv
import os

load_dotenv(override=True)
auth_code = os.getenv('WEBCRM_TOKEN').strip()
base_url = os.getenv('WEBCRM_BASE_URL').strip()

print('🔍 Finding the correct Products endpoint in webCRM...\n')

# Step 1: Get Access Token
print('Step 1: Getting Access Token...')
auth_response = requests.post(f'{base_url}/Auth/ApiLogin', data={'authCode': auth_code}, timeout=10)

if auth_response.status_code != 200:
    print(f'❌ Auth failed: {auth_response.text}')
    exit(1)

access_token = auth_response.json().get('AccessToken')
print(f'✅ Got Access Token\n')

headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json'
}

# Step 2: Test different product-related endpoints
endpoints_to_test = [
    '/Products',
    '/DeliveryProducts', 
    '/Articles',
    '/Items',
    '/Deliveries',
    '/ProductCatalog',
    '/Inventory'
]

print('Step 2: Testing product endpoints...\n')
print('='*60)

for endpoint in endpoints_to_test:
    try:
        url = f'{base_url}{endpoint}?page=1&size=5'
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 'N/A'
            print(f'✅ {endpoint:20} - Status: {response.status_code} - Items: {count}')
            
            # Show sample fields
            if isinstance(data, list) and len(data) > 0:
                sample = data[0]
                keys = list(sample.keys())[:5]  # First 5 fields
                print(f'   Sample fields: {", ".join(keys)}')
        elif response.status_code == 404:
            print(f'❌ {endpoint:20} - Not Found (404)')
        else:
            print(f'⚠️  {endpoint:20} - Status: {response.status_code}')
    except Exception as e:
        print(f'❌ {endpoint:20} - Error: {str(e)}')
    
    print('-'*60)

print('\n💡 Use the endpoint that returned data with product-like fields!')
