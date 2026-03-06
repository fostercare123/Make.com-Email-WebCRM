"""Quick script to check where buy@ayuguoky.com is located"""
from test_webcrm import WebCRMClient
import os
from dotenv import load_dotenv
import requests

load_dotenv()

BASE_URL = os.getenv('WEBCRM_BASE_URL')
TOKEN = os.getenv('WEBCRM_TOKEN')

# Get access token first
print("🔑 Getting access token...")
auth_response = requests.post(f"{BASE_URL}/Auth/ApiLogin", data={"authCode": TOKEN})
if auth_response.status_code != 200:
    print(f"❌ Auth failed: {auth_response.text}")
    exit(1)

ACCESS_TOKEN = auth_response.json()['AccessToken']
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}

# Search for the email
email = 'buy@ayuguoky.com'
print(f"\n🔍 Searching for: {email}")

persons_response = requests.get(f"{BASE_URL}/Persons", params={'PersonEmail': email}, headers=headers)
response_json = persons_response.json() if persons_response.status_code == 200 else {}

# Handle both possibilities: API might return {"data": [...]} or just [...]
if isinstance(response_json, dict):
    data = response_json.get('data', [])
else:
    data = response_json if isinstance(response_json, list) else []

print(f"✅ Found {len(data)} person(s)\n")

if len(data) == 0:
    print(f"❌ No person found with email {email}")
    print("This means Module 4 won't find anything and the flow will go through Route A (create new)")
else:
    for p in data:
        print(f"Person: {p.get('PersonFirstName')} {p.get('PersonLastName')}")
        print(f"  PersonId: {p.get('PersonId')}")
        print(f"  Email: {p.get('PersonEmail')}")
        print(f"  OrganisationId: {p.get('PersonOrganisationId')}")
        print()
        
        # Get the organization details
        if p.get('PersonOrganisationId'):
            org_response = requests.get(f"{BASE_URL}/Organisations/{p.get('PersonOrganisationId')}", headers=headers)
            org_json = org_response.json() if org_response.status_code == 200 else {}
            org_data = org_json.get('data', {}) if isinstance(org_json, dict) else org_json if isinstance(org_json, dict) else {}
            print(f"  THIS PERSON IS IN: '{org_data.get('OrganisationName')}'")
            print(f"  OrganisationId: {org_data.get('OrganisationId')}")
            print()

# Also search for "Spare parts request" company
print("\n🔍 Searching for 'Spare parts request' company")
spare_response = requests.get(f"{BASE_URL}/Organisations/Search", params={'term': 'Spare parts request'}, headers=headers)
spare_json = spare_response.json() if spare_response.status_code == 200 else {}

# Handle both possibilities
if isinstance(spare_json, dict):
    spare_data = spare_json.get('data', [])
else:
    spare_data = spare_json if isinstance(spare_json, list) else []
print(f"✅ Found {len(spare_data)} result(s)\n")

if len(spare_data) == 0:
    print("❌ 'Spare parts request' company NOT found!")
    print("This means Module 11 will return empty and Module 13 filter will fail")
else:
    for org in spare_data:
        print(f"Organisation: '{org.get('OrganisationName')}'")
        print(f"  OrganisationId: {org.get('OrganisationId')}")
        print()
        
print("\n" + "="*60)
print("DIAGNOSIS:")
print("="*60)
if len(data) > 0 and len(spare_data) > 0:
    person_org_id = data[0].get('PersonOrganisationId')
    spare_org_id = spare_data[0].get('OrganisationId')
    if person_org_id == spare_org_id:
        print("✅ Person IS in 'Spare parts request' company")
        print("   → Module 13 filter SHOULD pass")
        print("   → Should mark as Resigned + create new company + contact")
    else:
        print("❌ Person is NOT in 'Spare parts request' company")
        print(f"   Person OrgId: {person_org_id}")
        print(f"   Spare Parts OrgId: {spare_org_id}")
        print("   → Module 13 filter will FAIL (3rd condition)")
        print("   → Flow will stop after Module 12")
        print("\n💡 This is correct behavior - we don't want to mark as Resigned")
        print("   if they're in a different company!")
elif len(data) == 0:
    print("❌ Email not found in webCRM")
    print("   → Flow will take Route A (create new)")
elif len(spare_data) == 0:
    print("❌ 'Spare parts request' company not found")
    print("   → Module 13 filter will fail (1st condition)")
print("="*60)
