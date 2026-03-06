"""Quick debug: check webCRM API response format for Organisations"""
import requests, os, json
from dotenv import load_dotenv
load_dotenv(override=True)

base = os.getenv("WEBCRM_BASE_URL", "").strip()
token = os.getenv("WEBCRM_TOKEN", "").strip()

# Auth
r = requests.post(f"{base}/Auth/ApiLogin", data={"authCode": token})
at = r.json()["AccessToken"]
h = {"Authorization": f"Bearer {at}", "Content-Type": "application/json"}

# Fetch orgs page 1 (small sample)
r2 = requests.get(f"{base}/Organisations", headers=h, params={"page": 1, "size": 5})
orgs = r2.json()

if orgs:
    print("=== FIELD NAMES (first org) ===")
    for k in sorted(orgs[0].keys()):
        val = repr(orgs[0][k])[:80]
        print(f"  {k}: {val}")
    print(f"\nSample returned {len(orgs)} orgs")

# Fetch all and search
r3 = requests.get(f"{base}/Organisations", headers=h, params={"page": 1, "size": 1000})
all_orgs = r3.json()
print(f"\nTotal orgs on page 1: {len(all_orgs)}")

tekniko = [o for o in all_orgs if "TEKNIKO" in str(o.get("OrganisationName", ""))]
print(f"\n=== TEKNIKO matches ({len(tekniko)}) ===")
for o in tekniko:
    print(f"  ID={o.get('OrganisationId')} Name={o.get('OrganisationName')!r}")

spare = [o for o in all_orgs if "spare" in str(o.get("OrganisationName", "")).lower()]
print(f"\n=== Spare parts matches ({len(spare)}) ===")
for o in spare:
    print(f"  ID={o.get('OrganisationId')} Name={o.get('OrganisationName')!r}")

# Also show what Make.com sees - the raw HTTP response structure
print(f"\n=== Response type: {type(all_orgs).__name__} ===")
if isinstance(all_orgs, list) and all_orgs:
    print("Response is a plain array (not wrapped in 'data')")
elif isinstance(all_orgs, dict):
    print(f"Response is an object with keys: {list(all_orgs.keys())}")
