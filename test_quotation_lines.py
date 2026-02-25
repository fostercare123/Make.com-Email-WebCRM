#!/usr/bin/env python3
"""
Test to find item numbers in webCRM - possibly in Quotation Lines
"""
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv(override=True)
auth_code = os.getenv('WEBCRM_TOKEN').strip()
base_url = os.getenv('WEBCRM_BASE_URL').strip()

print('🔍 Checking webCRM Quotation Lines for item numbers...\n')

# Get Access Token
auth_response = requests.post(f'{base_url}/Auth/ApiLogin', data={'authCode': auth_code}, timeout=10)
access_token = auth_response.json().get('AccessToken')

headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json'
}

# Get all quotations (not organisation-specific)
print('Getting quotations...')
quotations_response = requests.get(f'{base_url}/Quotations?page=1&size=10', headers=headers, timeout=10)

if quotations_response.status_code == 200:
    quotations = quotations_response.json()
    print(f'✅ Found {len(quotations)} quotations\n')
    
    if quotations:
        first_quote = quotations[0]
        quote_id = first_quote.get('QuotationId')
        print(f'Using first quotation ID: {quote_id}\n')
        
        # Get quotation lines
        print('Getting quotation lines...')
        lines_url = f'{base_url}/Quotations/{quote_id}/QuotationLines?page=1&size=10'
        lines_response = requests.get(lines_url, headers=headers, timeout=10)
        
        if lines_response.status_code == 200:
            lines = lines_response.json()
            print(f'✅ Found {len(lines)} quotation lines\n')
            
            if lines:
                print('=' * 70)
                print('Sample Quotation Line:')
                print('=' * 70)
                sample = lines[0]
                print(json.dumps(sample, indent=2)[:2000])
                
                print('\n' + '=' * 70)
                print('Field names to look for item numbers:')
                print('=' * 70)
                for key in sorted(sample.keys()):
                    if 'item' in key.lower() or 'number' in key.lower() or 'product' in key.lower():
                        print(f'  ✅ {key}: {sample.get(key)}')
        else:
            print(f'❌ Failed to get quotation lines: {lines_response.status_code}')
            print(f'   URL: {lines_url}')
else:
    print(f'❌ Failed to get quotations: {quotations_response.status_code}')
