"""Fetch ALL persons (paginated) and search for the email"""
import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv('WEBCRM_BASE_URL')
TOKEN = os.getenv('WEBCRM_TOKEN')

# Get access token
auth_response = requests.post(f"{BASE_URL}/Auth/ApiLogin", data={"authCode": TOKEN})
ACCESS_TOKEN = auth_response.json()['AccessToken']
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}

email_to_find = 'buy@ayuguoky.com'

print(f"\n🔍 Searching for {email_to_find} in webCRM...\n")

# Fetch persons page by page
page = 1
found = False
total_checked = 0

while page <= 10:  # Check first 10 pages (500 persons)
    response = requests.get(f"{BASE_URL}/Persons", params={'page': page, 'size': 50}, headers=headers)
    data = response.json() if response.status_code == 200 else {}
    persons = data.get('data', []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
    
    if len(persons) == 0:
        break
    
    total_checked += len(persons)
    
    for person in persons:
        if person.get('PersonEmail', '').lower() == email_to_find.lower():
            print(f"✅ FOUND {email_to_find}!")
            print(f"   PersonId: {person.get('PersonId')}")
            print(f"   Name: {person.get('PersonFirstName')} {person.get('PersonLastName')}")
            print(f"   OrganisationId: {person.get('PersonOrganisationId')}")
            
            # Get the organization
            if person.get('PersonOrganisationId'):
                org_response = requests.get(f"{BASE_URL}/Organisations/{person.get('PersonOrganisationId')}", headers=headers)
                org_data = org_response.json() if org_response.status_code == 200 else {}
                org_info = org_data.get('data', {}) if isinstance(org_data, dict) else org_data
                print(f"   Organisation: {org_info.get('OrganisationName')}")
                print(f"   OrganisationId: {org_info.get('OrganisationId')}")
            
            found = True
            break
    
    if found:
        break
    
    page += 1

if not found:
    print(f"❌ {email_to_find} NOT found in first {total_checked} persons")
    print(f"\n💡 This explains why your flow is failing:")
    print(f"   1. Module 4 returns 50 persons (not filtered)")
    print(f"   2. Router sees length > 0 and triggers Route B")
    print(f"   3. But the email isn't actually in the results")
    print(f"   4. Module 13 filter fails because the specific email/org doesn't match")
    print(f"\n✅ SOLUTION: Fix Module 4 to properly filter by email")
