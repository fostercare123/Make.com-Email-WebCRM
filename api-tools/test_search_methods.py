"""Test different search methods for finding a person by email"""
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

email = 'buy@ayuguoky.com'

print(f"\n{'='*60}")
print(f"Testing search for: {email}")
print(f"{'='*60}\n")

# Test 1: /Persons?PersonEmail=
print("1️⃣ Testing: /Persons?PersonEmail=")
r1 = requests.get(f"{BASE_URL}/Persons", params={'PersonEmail': email}, headers=headers)
data1 = r1.json() if r1.status_code == 200 else {}
data1_list = data1.get('data', []) if isinstance(data1, dict) else (data1 if isinstance(data1, list) else [])
print(f"   Status: {r1.status_code}")
print(f"   Results: {len(data1_list)}")
if len(data1_list) > 0:
    print(f"   First result: {data1_list[0].get('PersonFirstName')} {data1_list[0].get('PersonLastName')} ({data1_list[0].get('PersonEmail')})")
print()

# Test 2: /Persons/Search?term=email
print("2️⃣ Testing: /Persons/Search?term=")
r2 = requests.get(f"{BASE_URL}/Persons/Search", params={'term': email}, headers=headers)
data2 = r2.json() if r2.status_code == 200 else {}
data2_list = data2.get('data', []) if isinstance(data2, dict) else (data2 if isinstance(data2, list) else [])
print(f"   Status: {r2.status_code}")
print(f"   Results: {len(data2_list)}")
if len(data2_list) > 0:
    for person in data2_list[:3]:
        print(f"     - {person.get('PersonFirstName')} {person.get('PersonLastName')} ({person.get('PersonEmail')})")
print()

# Test 3: /Persons with no filter (see default)
print("3️⃣ Testing: /Persons (no filter)")
r3 = requests.get(f"{BASE_URL}/Persons", headers=headers)
data3 = r3.json() if r3.status_code == 200 else {}
data3_list = data3.get('data', []) if isinstance(data3, dict) else (data3 if isinstance(data3, list) else [])
print(f"   Status: {r3.status_code}")
print(f"   Results: {len(data3_list)}")
print()

print(f"{'='*60}")
print("CONCLUSION:")
print(f"{'='*60}")
if len(data1_list) == len(data3_list):
    print("❌ PersonEmail parameter does NOT filter results")
    print("   /Persons?PersonEmail= returns same count as /Persons")
if len(data2_list) > 0 and len(data2_list) < len(data1_list):
    print("✅ /Persons/Search?term= DOES filter results")
    print(f"   Found {len(data2_list)} matches for '{email}'")
    print("\n💡 SOLUTION: Module 4 should use /Persons/Search?term={{email}}")
print(f"{'='*60}")
