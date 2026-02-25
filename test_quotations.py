#!/usr/bin/env python3
"""
Test to explore webCRM Companies > Quotations > Lines structure
and find how to match item numbers
"""
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv(override=True)
auth_code = os.getenv('WEBCRM_TOKEN').strip()
base_url = os.getenv('WEBCRM_BASE_URL').strip()

print('🔍 Exploring webCRM Companies > Quotations > Quotation Lines...\n')

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

# Step 2: Get all organisations to find "Testkunde"
print('Step 2: Getting all organisations...')
orgs_response = requests.get(f'{base_url}/Organisations?page=1&size=250', headers=headers, timeout=10)

if orgs_response.status_code != 200:
    print(f'❌ Failed to get organisations: {orgs_response.text}')
    exit(1)

organisations = orgs_response.json()
print(f'✅ Found {len(organisations)} organisations\n')

# Find Testkunde
testkunde = None
for org in organisations:
    if 'Testkunde' in org.get('OrganisationName', ''):
        testkunde = org
        print(f"✅ Found Testkunde:")
        print(f"   ID: {org['OrganisationId']}")
        print(f"   Name: {org['OrganisationName']}\n")
        break

if not testkunde:
    print("❌ Testkunde not found. Available organisations:")
    for org in organisations[:10]:
        print(f"   - {org['OrganisationName']}")
    exit(1)

testkunde_id = testkunde['OrganisationId']

# Step 3: Get quotations for this organisation
print(f'Step 3: Getting quotations for {testkunde["OrganisationName"]}...')
quotations_response = requests.get(
    f'{base_url}/Organisations/{testkunde_id}/Quotations?page=1&size=250',
    headers=headers,
    timeout=10
)

if quotations_response.status_code == 200:
    quotations = quotations_response.json()
    print(f'✅ Found {len(quotations)} quotations\n')
    
    if quotations:
        for i, quote in enumerate(quotations[:3], 1):
            print(f'Quotation {i}:')
            print(f'  ID: {quote.get("QuotationId")}')
            print(f'  Number: {quote.get("QuotationNumber")}')
            print(f'  Name: {quote.get("QuotationName", quote.get("Name", "N/A"))}')
            
            quotation_id = quote.get('QuotationId')
            
            # Step 4: Get quotation lines for this quotation
            print(f'\n  Getting quotation lines...')
            lines_response = requests.get(
                f'{base_url}/Organisations/{testkunde_id}/Quotations/{quotation_id}/QuotationLines?page=1&size=250',
                headers=headers,
                timeout=10
            )
            
            if lines_response.status_code == 200:
                lines = lines_response.json()
                print(f'  ✅ Found {len(lines)} quotation lines')
                
                if lines:
                    print(f'\n  Sample Quotation Line Fields:')
                    sample_line = lines[0]
                    for key in list(sample_line.keys())[:10]:
                        print(f'    - {key}: {sample_line.get(key)}')
                    
                    # Look for item number field
                    print(f'\n  Checking for item number fields...')
                    all_keys = set()
                    for line in lines:
                        all_keys.update(line.keys())
                    
                    item_fields = [k for k in all_keys if 'item' in k.lower() or 'number' in k.lower()]
                    if item_fields:
                        print(f'  Found potential item/number fields:')
                        for field in item_fields:
                            print(f'    - {field}')
                    
                    print(f'\n  First quotation line details:')
                    print(json.dumps(lines[0], indent=2)[:500])
            else:
                print(f'  ❌ Failed to get quotation lines: {lines_response.status_code}')
            
            print(f'\n{"-"*60}\n')
            break
else:
    print(f'❌ Failed to get quotations: {quotations_response.status_code}')
    print(f'   Response: {quotations_response.text}')

print('\n💡 Now we know the structure for matching item numbers in quotation lines!')
