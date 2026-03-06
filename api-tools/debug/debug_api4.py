"""Test if webCRM allows larger page sizes"""
import requests, os
from dotenv import load_dotenv
load_dotenv(override=True)

base = os.getenv("WEBCRM_BASE_URL", "").strip()
token = os.getenv("WEBCRM_TOKEN", "").strip()

r = requests.post(f"{base}/Auth/ApiLogin", data={"authCode": token}, timeout=15)
at = r.json()["AccessToken"]
h = {"Authorization": f"Bearer {at}", "Content-Type": "application/json"}

for size in [2000, 3000, 5000, 10000]:
    r = requests.get(f"{base}/Organisations", headers=h, params={"page": 1, "size": size}, timeout=30)
    if r.status_code == 200:
        data = r.json()
        count = len(data) if isinstance(data, list) else "?"
        tekniko = [o for o in data if "TEKNIKO" in str(o.get("OrganisationName", ""))] if isinstance(data, list) else []
        print(f"  size={size:6d} -> {count} orgs, TEKNIKO found: {len(tekniko)}")
    else:
        print(f"  size={size:6d} -> HTTP {r.status_code}")

print()
for size in [2000, 5000, 10000]:
    r = requests.get(f"{base}/Persons", headers=h, params={"page": 1, "size": size}, timeout=30)
    if r.status_code == 200:
        data = r.json()
        count = len(data) if isinstance(data, list) else "?"
        print(f"  size={size:6d} -> {count} persons")
    else:
        print(f"  size={size:6d} -> HTTP {r.status_code}")
