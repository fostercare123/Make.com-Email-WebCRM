"""Test various webCRM API filtering/search approaches"""
import requests, os
from dotenv import load_dotenv
load_dotenv(override=True)

base = os.getenv("WEBCRM_BASE_URL", "").strip()
token = os.getenv("WEBCRM_TOKEN", "").strip()

# Auth
r = requests.post(f"{base}/Auth/ApiLogin", data={"authCode": token}, timeout=15)
at = r.json()["AccessToken"]
h = {"Authorization": f"Bearer {at}", "Content-Type": "application/json"}

# --- Test 1: /Persons/Search with different terms ---
print("=== /Persons/Search ===")
for term in ["vnn@eilersen.com", "vnn", "Nikolic", "test2@example.com"]:
    r = requests.get(f"{base}/Persons/Search", headers=h, params={"term": term}, timeout=15)
    data = r.json() if r.status_code == 200 else []
    count = len(data) if isinstance(data, list) else "?"
    print(f"  term={term!r:30s} -> {count} results")

# --- Test 2: /Persons with field filter in query params ---
print("\n=== /Persons with query filters ===")
for params in [
    {"PersonEmail": "vnn@eilersen.com", "page": 1, "size": 10},
    {"email": "vnn@eilersen.com", "page": 1, "size": 10},
    {"search": "vnn@eilersen.com", "page": 1, "size": 10},
]:
    r = requests.get(f"{base}/Persons", headers=h, params=params, timeout=15)
    data = r.json() if r.status_code == 200 else []
    count = len(data) if isinstance(data, list) else "?"
    print(f"  params={params!r:60s} -> {r.status_code}, {count} results")

# --- Test 3: /Organisations/Search ---
print("\n=== /Organisations/Search ===")
for term in ["TEKNIKO", "Spare parts", "Webcrm", "webcrm"]:
    r = requests.get(f"{base}/Organisations/Search", headers=h, params={"term": term}, timeout=15)
    data = r.json() if r.status_code == 200 else []
    count = len(data) if isinstance(data, list) else "?"
    print(f"  term={term!r:30s} -> {count} results")

# --- Test 4: /Organisations with field filter  ---
print("\n=== /Organisations with query filters ===")
for params in [
    {"OrganisationName": "TEKNIKO Holding", "page": 1, "size": 10},
    {"name": "TEKNIKO Holding", "page": 1, "size": 10},
    {"search": "TEKNIKO", "page": 1, "size": 10},
]:
    r = requests.get(f"{base}/Organisations", headers=h, params=params, timeout=15)
    data = r.json() if r.status_code == 200 else []
    count = len(data) if isinstance(data, list) else "?"
    print(f"  params={params!r:60s} -> {r.status_code}, {count} results")

# --- Test 5: POST-based search if exists ---
print("\n=== POST /Organisations/Search ===")
for body in [
    {"OrganisationName": "TEKNIKO Holding"},
    {"term": "TEKNIKO"},
]:
    r = requests.post(f"{base}/Organisations/Search", headers=h, json=body, timeout=15)
    data = r.json() if r.status_code == 200 else r.text[:100]
    count = len(data) if isinstance(data, list) else data
    print(f"  body={body!r:50s} -> {r.status_code}, {count}")

# --- Test 6: Check last page for TEKNIKO ---
print("\n=== Last page of Organisations (where new ones would be) ===")
r = requests.get(f"{base}/Organisations", headers=h, params={"page": 5, "size": 1000}, timeout=30)
data = r.json() if r.status_code == 200 else []
if isinstance(data, list):
    tekniko = [o for o in data if "TEKNIKO" in str(o.get("OrganisationName", ""))]
    print(f"  Page 5: {len(data)} orgs, TEKNIKO matches: {len(tekniko)}")
    for o in tekniko:
        print(f"    ID={o.get('OrganisationId')} Name={o.get('OrganisationName')!r}")
