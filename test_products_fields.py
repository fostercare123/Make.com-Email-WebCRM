#!/usr/bin/env python3
"""
Simple test to check Products endpoint fields and search capabilities
"""
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv(override=True)
auth_code = os.getenv('WEBCRM_TOKEN').strip()
base_url = os.getenv('WEBCRM_BASE_URL').strip()

print('🔍 Checking webCRM Products endpoint structure...\n')

# Get Access Token
auth_response = requests.post(f'{base_url}/Auth/ApiLogin', data={'authCode': auth_code}, timeout=10)
access_token = auth_response.json().get('AccessToken')

headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json'
}

# Get products
print('Getting first 3 products...\n')
products_response = requests.get(f'{base_url}/Products?page=1&size=3', headers=headers, timeout=10)

if products_response.status_code == 200:
    products = products_response.json()
    print(f'✅ Found {len(products)} products\n')
    
    if products:
        print('=' * 60)
        for i, product in enumerate(products, 1):
            print(f'\nProduct {i}:')
            print(f'  ProductId: {product.get("ProductId")}')
            print(f'  ProductNumber: {product.get("ProductNumber")}')
            print(f'  ProductName: {product.get("ProductName")}')
            print(f'  ProductCostPrice: {product.get("ProductCostPrice")}')
            print(f'  ProductSalesPrice: {product.get("ProductSalesPrice")}')
            
            # Show all fields
            print(f'\n  All available fields:')
            for key in sorted(product.keys()):
                value = product[key]
                if value is not None and str(value).strip():
                    print(f'    - {key}')
        
        print('\n' + '=' * 60)
        print('\n💡 Key observations:')
        print('  - ProductNumber: This could match your Uniconta ItemNumber')
        print('  - ProductId: Unique identifier in webCRM')
        print('  - You can search by ProductNumber if needed')
else:
    print(f'❌ Failed: {products_response.status_code}')
