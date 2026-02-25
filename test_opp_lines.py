#!/usr/bin/env python3
import requests, os, json
from dotenv import load_dotenv

load_dotenv()
auth = requests.post(f'{os.getenv("WEBCRM_BASE_URL")}/Auth/ApiLogin', data={'authCode': os.getenv('WEBCRM_TOKEN')}).json()
h = {'Authorization': f'Bearer {auth["AccessToken"]}', 'Accept': 'application/json'}

print('Testing OpportunityLines endpoint...\n')
r = requests.get(f'{os.getenv("WEBCRM_BASE_URL")}/OpportunityLines?page=1&size=5', headers=h)
print(f'Status: {r.status_code}')

if r.status_code == 200:
    lines = r.json()
    print(f'Found {len(lines)} OpportunityLines\n')
    
    if lines:
        line = lines[0]
        print('Sample OpportunityLine fields:')
        for k in sorted(line.keys()):
            v = str(line[k])[:40]
            if line[k]:
                print(f'  {k}: {v}')
else:
    print(f'Error: {r.text[:200]}')
