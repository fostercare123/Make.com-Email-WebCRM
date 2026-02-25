#!/usr/bin/env python3
import requests, os
from dotenv import load_dotenv
load_dotenv(override=True)

auth_code = os.getenv('WEBCRM_TOKEN').strip()
base_url = os.getenv('WEBCRM_BASE_URL').strip()

auth = requests.post(f'{base_url}/Auth/ApiLogin', data={'authCode': auth_code}).json()
h = {'Authorization': f'Bearer {auth["AccessToken"]}', 'Accept': 'application/json'}

# Get first opportunity
opp = requests.get(f'{base_url}/Opportunities?page=1&size=1', headers=h).json()[0]
print(f"Opportunity {opp['OpportunityId']}:")
for k in sorted(opp.keys()):
    if str(opp[k])[:20].strip():
        print(f"  {k}")
