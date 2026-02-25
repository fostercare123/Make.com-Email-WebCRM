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

# Get opportunities
print('Getting Opportunities...\n')
opp_resp = requests.get(f'{base_url}/Opportunities?page=1&size=5', headers=headers, timeout=10)
opps = opp_resp.json() if opp_resp.status_code == 200 else []
print(f'Found {len(opps)} opportunities\n')

if opps:
    opp = opps[0]
    opp_id = opp.get('OpportunityId')
    print('=' * 70)
    print('OPPORTUNITY STRUCTURE:')
    print('=' * 70)
    print(json.dumps(opp, indent=2)[:2000])
    
    print('\n' + '=' * 70)
    print('CHECKING FOR PRODUCT/LINE ITEMS:')
    print('=' * 70)
    
    # Look for line items
    all_keys = opp.keys()
    product_keys = [k for k in all_keys if 'line' in k.lower() or 'item' in k.lower()]
    
    if product_keys:
        print('Found product/line related fields:')
        for key in product_keys:
            print(f'  - {key}: {opp.get(key)}')
    else:
        print('No line items found in Opportunity - checking for line endpoint...')
        
        # Try to get opportunity lines
        test_urls = [
            f'/Opportunities/{opp_id}/Lines',
            f'/Opportunities/{opp_id}/OpportunityLines',
            f'/Opportunities/{opp_id}/Products',
            f'/OpportunityLines',
        ]
        
        for url in test_urls:
            try:
                test_resp = requests.get(f'{base_url}{url}?page=1&size=10', headers=headers, timeout=5)
                if test_resp.status_code == 200:
                    print(f'\n✅ Found endpoint: {url}')
                    data = test_resp.json()
                    print(f'   Items: {len(data)}')
                    if data:
                        print(f'   First item:')
                        print(json.dumps(data[0], indent=2)[:500])
            except:
                pass
