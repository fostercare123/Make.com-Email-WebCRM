"""Check total counts and test search endpoints"""
import requests, os, json
from dotenv import load_dotenv
load_dotenv(override=True)

base = os.getenv("WEBCRM_BASE_URL", "").strip()
token = os.getenv("WEBCRM_TOKEN", "").strip()

# Auth
r = requests.post(f"{base}/Auth/ApiLogin", data={"authCode": token})
at = r.json()["AccessToken"]
h = {"Authorization": f"Bearer {at}", "Content-Type": "application/json"}

# Count pages of Organisations
print("=== Organisation page counts ===")
for page in [1, 2, 3, 4, 5]:
    r = requests.get(f"{base}/Organisations", headers=h, params={"page": page, "size": 1000})
    data = r.json()
    count = len(data) if isinstance(data, list) else 0
    print(f"  Page {page}: {count} orgs")
    if count == 0:
        break

# Count pages of Persons
print("\n=== Person page counts ===")
for page in [1, 2, 3, 4, 5]:
    r = requests.get(f"{base}/Persons", headers=h, params={"page": page, "size": 1000})
    data = r.json()
    count = len(data) if isinstance(data, list) else 0
    print(f"  Page {page}: {count} orgs")
    if count == 0:
        break

# Try search endpoints
print("\n=== Testing /Organisations/Search ===")
r = requests.get(f"{base}/Organisations/Search", headers=h, params={"term": "TEKNIKO"})
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    if isinstance(data, list):
        print(f"  Results: {len(data)}")
        for o in data[:5]:
            print(f"    ID={o.get('OrganisationId')} Name={o.get('OrganisationName')!r}")
    else:
        print(f"  Response: {str(data)[:200]}")
else:
    print(f"  Body: {r.text[:200]}")

print("\n=== Testing /Persons/Search for vnn@eilersen.com ===")
r = requests.get(f"{base}/Persons/Search", headers=h, params={"term": "vnn@eilersen.com"})
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    if isinstance(data, list):
        print(f"  Results: {len(data)}")
        for p in data[:5]:
            print(f"    ID={p.get('PersonId')} Email={p.get('PersonEmail')!r} OrgID={p.get('PersonOrganisationId')}")

# Also try searching TEKNIKO across all pages
print("\n=== Searching all pages for TEKNIKO ===")
for page in [1, 2, 3, 4, 5]:
    r = requests.get(f"{base}/Organisations", headers=h, params={"page": page, "size": 1000})
    data = r.json()
    if not isinstance(data, list) or len(data) == 0:
        break
    matches = [o for o in data if "TEKNIKO" in str(o.get("OrganisationName", ""))]
    if matches:
        for o in matches:
            print(f"  Page {page}: ID={o.get('OrganisationId')} Name={o.get('OrganisationName')!r}")
print("  Done")
