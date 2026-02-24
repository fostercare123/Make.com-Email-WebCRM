# test_webcrm.py
# Full script with debugging, token cleaning, and sys import fixed

import requests
from dotenv import load_dotenv
import os
import sys  # ← Added this line to fix the NameError

# ────────────────────────────────────────────────
# Load environment variables from .env file
load_dotenv()

BASE_URL = os.getenv("WEBCRM_BASE_URL")
TOKEN    = os.getenv("WEBCRM_TOKEN")

# Aggressive cleaning of the token
clean_token = TOKEN.strip() if TOKEN else ""

# ────────────────────────────────────────────────
# Debug: Show exactly what we loaded
print("=== DEBUG: .env LOADING ===")
print("BASE_URL:", BASE_URL)
print("Original TOKEN length:", len(TOKEN) if TOKEN else "None")
print("Cleaned token length:", len(clean_token))
print("Cleaned token prefix (first 15 chars):", clean_token[:15] + "..." if len(clean_token) > 15 else clean_token)
print("Cleaned token suffix (last 10 chars):", "..." + clean_token[-10:] if len(clean_token) > 10 else clean_token)
print("=================================\n")

if not BASE_URL or not clean_token:
    print("ERROR: Missing WEBCRM_BASE_URL or WEBCRM_TOKEN in .env file")
    print("Make sure .env contains exactly:")
    print("WEBCRM_BASE_URL=https://api.webcrm.com")
    print("WEBCRM_TOKEN=your-36-character-token-here")
    exit(1)

# ────────────────────────────────────────────────
# Headers – exact format that worked in Postman (Bearer + space + token)
HEADERS = {
    "Authorization": "Bearer " + clean_token,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Debug: Show the EXACT header that will be sent
print("=== DEBUG: HEADERS THAT WILL BE SENT ===")
print("Authorization header (repr):", repr(HEADERS["Authorization"]))
print("Authorization length:", len(HEADERS["Authorization"]))
print("Other headers:", {k: v for k, v in HEADERS.items() if k != "Authorization"})
print("=================================\n")

# ────────────────────────────────────────────────
def get_organisations(page=1, size=20):
    """Fetch organisations from webCRM API"""
    url = f"{BASE_URL}/Organisations?page={page}&size={size}"
    
    print(f"Requesting: {url}")
    print("Sending request now...\n")

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Success! Found {len(data)} organisations on page {page}")
                if data:
                    print("\nFirst organisation (keys only):")
                    print(list(data[0].keys()))
                    print("\nExample name:", data[0].get("OrganisationName", "N/A"))
                    print("Example email:", data[0].get("OrganisationEmail", "N/A"))
                else:
                    print("No organisations found (empty list)")
            except ValueError:
                print("Response was 200 but not valid JSON")
                print("Response body preview:", response.text[:500])
        else:
            print("Request failed.")
            print("Response body preview:", response.text[:800] or "[empty]")
            print("Full headers sent:", HEADERS)
        
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print("Connection/request error:", str(e))
        return False


# ────────────────────────────────────────────────
if __name__ == "__main__":
    print("Starting webCRM API test...")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"requests version: {requests.__version__}\n")
    
    success = get_organisations(page=1, size=20)
    
    if success:
        print("\nSUCCESS! Connection works → we can now add search/create/update.")
    else:
        print("\nFailed. Check token freshness, permissions, or recreate the token in webCRM.")