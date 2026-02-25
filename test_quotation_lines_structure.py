#!/usr/bin/env python3
"""
Test to understand webCRM Quotation Lines API structure
Map the UI fields to API field names
"""
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv(override=True)
auth_code = os.getenv('WEBCRM_TOKEN').strip()
base_url = os.getenv('WEBCRM_BASE_URL').strip()

print('🔍 Exploring webCRM Quotation Lines API structure...\n')

# Get Access Token
auth_response = requests.post(f'{base_url}/Auth/ApiLogin', data={'authCode': auth_code}, timeout=10)
if auth_response.status_code != 200:
    print(f'❌ Auth failed')
    exit(1)

access_token = auth_response.json().get('AccessToken')

headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json'
}

# Step 1: Get first organisation
print('Step 1: Getting first organisation...')
orgs_response = requests.get(f'{base_url}/Organisations?page=1&size=1', headers=headers, timeout=10)

if orgs_response.status_code == 200:
    orgs = orgs_response.json()
    if orgs:
        org_id = orgs[0]['OrganisationId']
        org_name = orgs[0].get('OrganisationName', 'Unknown')
        print(f'✅ Using organisation: {org_name} (ID: {org_id})\n')
        
        # Step 2: Get quotations for this org
        print('Step 2: Getting quotations for this organisation...')
        quotes_url = f'{base_url}/Organisations/{org_id}/Quotations?page=1&size=10'
        quotes_response = requests.get(quotes_url, headers=headers, timeout=10)
        
        if quotes_response.status_code == 200:
            quotes = quotes_response.json()
            print(f'✅ Found {len(quotes)} quotations\n')
            
            if quotes:
                quote_id = quotes[0]['QuotationId']
                print(f'Step 3: Getting quotation lines for quotation {quote_id}...')
                
                # Step 3: Get quotation lines
                lines_url = f'{base_url}/Organisations/{org_id}/Quotations/{quote_id}/QuotationLines?page=1&size=50'
                lines_response = requests.get(lines_url, headers=headers, timeout=10)
                
                if lines_response.status_code == 200:
                    lines = lines_response.json()
                    print(f'✅ Found {len(lines)} quotation lines\n')
                    
                    if lines:
                        print('=' * 80)
                        print('QUOTATION LINE STRUCTURE')
                        print('=' * 80)
                        
                        sample = lines[0]
                        print('\nAll available fields:')
                        for i, key in enumerate(sorted(sample.keys()), 1):
                            value = sample[key]
                            display_value = str(value)[:50]
                            print(f'{i:2}. {key:40} = {display_value}')
                        
                        print('\n' + '=' * 80)
                        print('KEY FIELDS FOR YOUR USE CASE:')
                        print('=' * 80)
                        
                        # Look for item number field
                        item_fields = [k for k in sample.keys() if 'item' in k.lower() or 'number' in k.lower()]
                        price_fields = [k for k in sample.keys() if 'price' in k.lower()]
                        quantity_fields = [k for k in sample.keys() if 'quantity' in k.lower()]
                        
                        if item_fields:
                            print(f'\n📦 Item/Number fields:')
                            for field in item_fields:
                                print(f'  - {field}: {sample.get(field)}')
                        
                        if price_fields:
                            print(f'\n💰 Price fields:')
                            for field in price_fields:
                                print(f'  - {field}: {sample.get(field)}')
                        
                        if quantity_fields:
                            print(f'\n📊 Quantity fields:')
                            for field in quantity_fields:
                                print(f'  - {field}: {sample.get(field)}')
                        
                        print('\n' + '=' * 80)
                        print('FULL FIRST QUOTATION LINE (JSON):')
                        print('=' * 80)
                        print(json.dumps(sample, indent=2))
                    else:
                        print('❌ No quotation lines found')
                else:
                    print(f'❌ Failed to get quotation lines: {lines_response.status_code}')
            else:
                print('❌ No quotations found')
        else:
            print(f'❌ Failed to get quotations: {quotes_response.status_code}')
            print(f'   URL: {quotes_url}')
            print(f'   Response: {quotes_response.text[:200]}')
    else:
        print('❌ No organisations found')
else:
    print(f'❌ Failed to get organisations: {orgs_response.status_code}')
