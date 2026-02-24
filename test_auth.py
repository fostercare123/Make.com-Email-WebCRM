#!/usr/bin/env python3
"""
Test WebCRM Authentication and fetch companies
"""
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv(override=True)
auth_code = os.getenv('WEBCRM_TOKEN').strip()
base_url = os.getenv('WEBCRM_BASE_URL').strip()

print('Step 1: Getting Access Token...\n')
auth_response = requests.post(f'{base_url}/Auth/ApiLogin', data={'authCode': auth_code}, timeout=10)
print(f'Auth Status: {auth_response.status_code}')

if auth_response.status_code == 200:
    auth_data = auth_response.json()
    access_token = auth_data.get('AccessToken')
    
    print(f'✅ Got Access Token: {access_token[:20]}...')
    print(f'   Expires in: {auth_data.get("ExpiresIn")} seconds')
    
    print('\nStep 2: Using Access Token to fetch Organisations...\n')
    headers = {'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
    org_response = requests.get(f'{base_url}/Organisations?page=1&size=5', headers=headers, timeout=10)
    
    print(f'Organisations Status: {org_response.status_code}')
    if org_response.status_code == 200:
        orgs = org_response.json()
        print(f'✅ SUCCESS! Found {len(orgs)} organisations:')
        for i, org in enumerate(orgs[:3], 1):
            org_name = org.get('OrganisationName', 'N/A')
            org_id = org.get('OrganisationId', 'N/A')
            print(f'   {i}. {org_name} (ID: {org_id})')
    else:
        print(f'Error: {org_response.text}')
else:
    print(f'Error: {auth_response.text}')
