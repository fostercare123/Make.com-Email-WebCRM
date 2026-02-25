#!/usr/bin/env python3
import requests
from dotenv import load_dotenv
import os

load_dotenv(override=True)
auth_code = os.getenv('WEBCRM_TOKEN').strip()
base_url = os.getenv('WEBCRM_BASE_URL').strip()

# Get token
auth_response = requests.post(f'{base_url}/Auth/ApiLogin', data={'authCode': auth_code}, timeout=10)
access_token = auth_response.json().get('AccessToken')
headers = {'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}

# Get opportunities
opp_resp = requests.get(f'{base_url}/Opportunities?page=1&size=1', headers=headers, timeout=10)
opps = opp_resp.json()
opp = opps[0]
opp_id = opp.get('OpportunityId')

print(f'Opportunity ID: {opp_id}\n')
print('ALL FIELDS IN OPPORTUNITY:')
print('=' * 70)

for key in sorted(opp.keys()):
    value = opp[key]
    if value is not None and str(value) != '':
        display = str(value)[:60]
        print(f'{key:50} = {display}')

print('\n' + '=' * 70)
print('Fields with "Product", "Line", or "Item":')
print('=' * 70)
relevant = [k for k in opp.keys() if 'product' in k.lower() or 'line' in k.lower() or 'item' in k.lower()]
for key in relevant:
    print(f'  {key}: {opp[key]}')

# Now try to get line items
print('\n' + '=' * 70)
print('Trying to access OpportunityLines...')
print('=' * 70)

urls_to_try = [
    f'/Opportunities/{opp_id}/OpportunityLines',
    f'/OpportunityLines?OpportunityId={opp_id}',
]

for url in urls_to_try:
    full_url = f'{base_url}{url}'
    print(f'\nTrying: {url}')
    resp = requests.get(full_url, headers=headers, timeout=10)
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200 and resp.text:
        data = resp.json()
        print(f'Found {len(data)} items')
        if data:
            print(f'First item keys: {list(data[0].keys())[:10]}')
