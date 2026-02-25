#!/usr/bin/env python3
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv(override=True)
auth_code = os.getenv('WEBCRM_TOKEN').strip()
base_url = os.getenv('WEBCRM_BASE_URL').strip()

# Get token
auth_response = requests.post(f'{base_url}/Auth/ApiLogin', data={'authCode': auth_code}, timeout=10)
access_token = auth_response.json().get('AccessToken')
headers = {'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}

# Test different quotation endpoints
test_urls = [
    '/Quotations',
    '/Opportunities',
    '/Organisations/1/Opportunities',
]

for url in test_urls:
    test_url = f'{base_url}{url}?page=1&size=1'
    resp = requests.get(test_url, headers=headers, timeout=10)
    print(f'{url:40} - Status: {resp.status_code}')
    
    if resp.status_code == 200 and resp.text:
        data = resp.json()
        print(f'  Found {len(data)} items')
        if data:
            item = data[0]
            # Look for item/product related fields
            product_fields = [k for k in item.keys() if 'item' in k.lower() or 'product' in k.lower() or 'line' in k.lower()]
            print(f'  Fields with item/product/line: {product_fields}')
    print()
