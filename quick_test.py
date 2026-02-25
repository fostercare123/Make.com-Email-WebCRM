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

# Get first org
orgs_resp = requests.get(f'{base_url}/Organisations?page=1&size=1', headers=headers, timeout=10)
print(f'Organisations Status: {orgs_resp.status_code}')
if orgs_resp.status_code != 200:
    print(f'Error: {orgs_resp.text}')
    exit(1)

orgs = orgs_resp.json()
org_id = orgs[0]['OrganisationId']
print(f'Using Org ID: {org_id}\n')

# Get quotations for this org
quotes_url = f'{base_url}/Organisations/{org_id}/Quotations?page=1&size=10'
quotes_resp = requests.get(quotes_url, headers=headers, timeout=10)
print(f'Quotations URL: {quotes_url}')
print(f'Quotations Status: {quotes_resp.status_code}')
if quotes_resp.status_code != 200:
    print(f'Error: {quotes_resp.text}')
    exit(1)

quotes_json = quotes_resp.json() if quotes_resp.text else []
print(f'Found {len(quotes_json)} quotations')

if not quotes_json:
    print('No quotations found for this organisation')
    exit(1)

quote_id = quotes_json[0]['QuotationId']
print(f'Using Quote ID: {quote_id}\n')

# Get quotation lines
lines_url = f'{base_url}/Organisations/{org_id}/Quotations/{quote_id}/QuotationLines?page=1&size=50'
lines_resp = requests.get(lines_url, headers=headers, timeout=10)
print(f'QuotationLines URL: {lines_url}')
print(f'QuotationLines Status: {lines_resp.status_code}')
if lines_resp.status_code != 200:
    print(f'Error: {lines_resp.text}')
    exit(1)

lines = lines_resp.json() if lines_resp.text else []
print(f'Found {len(lines)} quotation lines\n')

if lines:
    line = lines[0]
    print('=' * 70)
    print('FIRST QUOTATION LINE - ALL FIELDS:')
    print('=' * 70)
    print(json.dumps(line, indent=2))
else:
    print('No quotation lines found')
