"""
test_webcrm.py - Simple WebCRM API Connection Tester

This script provides a simple interface to test WebCRM API endpoints.
Similar to Postman, but in pure Python code.

Usage:
    python test_webcrm.py
"""

import requests
from dotenv import load_dotenv
import os
import sys
import json
from typing import Optional, Dict, Any

# Load environment variables from .env file
load_dotenv()

# Configuration
BASE_URL = os.getenv("WEBCRM_BASE_URL", "").strip()
TOKEN = os.getenv("WEBCRM_TOKEN", "").strip()

# Validate configuration
if not BASE_URL or not TOKEN:
    print("❌ ERROR: Missing WEBCRM_BASE_URL or WEBCRM_TOKEN in .env file")
    print("\nMake sure .env contains:")
    print("  WEBCRM_BASE_URL=https://api.webcrm.com")
    print("  WEBCRM_TOKEN=your-36-character-token-here")
    sys.exit(1)

# ────────────────────────────────────────────────
# API Client Class
class WebCRMClient:
    """Simple WebCRM API client for testing endpoints"""
    
    def __init__(self, base_url: str, token: str, debug: bool = True):
        self.base_url = base_url.rstrip("/")
        self.token = token.strip()
        self.debug = debug
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def _print_debug(self, title: str, content: str):
        """Print debug information if debug mode is enabled"""
        if self.debug:
            print(f"  ℹ️  [{title}] {content}")
    
    def _print_request(self, method: str, url: str):
        """Print request details"""
        if self.debug:
            print(f"\n📤 {method} {url}")
    
    def _print_response(self, status_code: int, response_text: str = "", is_json: bool = False):
        """Print response details"""
        if self.debug:
            status_symbol = "✅" if 200 <= status_code < 300 else "❌"
            print(f"📥 {status_symbol} Status: {status_code}")
            if response_text and len(response_text) < 500:
                print(f"   {response_text[:500]}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Generic method to make API requests"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            self._print_request(method, url)
            
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=15)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data, timeout=15)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers, timeout=15)
            else:
                print(f"❌ Unsupported HTTP method: {method}")
                return None
            
            self._print_response(response.status_code, response.text)
            
            # Handle successful responses
            if response.status_code in (200, 201, 204):
                if response.text:
                    return response.json()
                return {"status": "success", "code": response.status_code}
            else:
                print(f"❌ Request failed with status {response.status_code}")
                if response.text:
                    try:
                        print("   Error details:", json.dumps(response.json(), indent=2))
                    except json.JSONDecodeError:
                        print(f"   Response: {response.text[:500]}")
                return None
        
        except requests.exceptions.Timeout:
            print("❌ Request timeout (15s exceeded)")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {str(e)}")
            return None
    
    # ────────────────────────────────────────────────
    # API Methods (Examples)
    
    def get_organisations(self, page: int = 1, size: int = 20) -> Optional[list]:
        """Fetch organisations"""
        result = self._make_request("GET", "/Organisations", params={"page": page, "size": size})
        if result:
            print(f"✅ Found {len(result)} organisations")
            if result:
                self._print_debug("Sample", f"Name: {result[0].get('OrganisationName', 'N/A')}")
        return result
    
    def get_organisation_by_id(self, org_id: str) -> Optional[Dict]:
        """Fetch a single organisation"""
        result = self._make_request("GET", f"/Organisations/{org_id}")
        if result:
            print(f"✅ Organisation retrieved")
            self._print_debug("Name", result.get("OrganisationName", "N/A"))
        return result
    
    def get_opportunities(self, page: int = 1, size: int = 20) -> Optional[list]:
        """Fetch opportunities"""
        result = self._make_request("GET", "/Opportunities", params={"page": page, "size": size})
        if result:
            print(f"✅ Found {len(result)} opportunities")
        return result
    
    def get_opportunity_by_id(self, opp_id: str) -> Optional[Dict]:
        """Fetch a single opportunity"""
        result = self._make_request("GET", f"/Opportunities/{opp_id}")
        if result:
            print(f"✅ Opportunity retrieved")
            self._print_debug("Title", result.get("Name", "N/A"))
        return result
    
    def get_persons(self, org_id: Optional[str] = None, page: int = 1, size: int = 20) -> Optional[list]:
        """Fetch persons (optionally filtered by organisation)"""
        endpoint = f"/Organisations/{org_id}/Persons" if org_id else "/Persons"
        result = self._make_request("GET", endpoint, params={"page": page, "size": size})
        if result:
            print(f"✅ Found {len(result)} persons")
        return result
    
    def create_person(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new person"""
        result = self._make_request("POST", "/Persons", data=data)
        if result:
            print(f"✅ Person created")
        return result
    
    def test_connection(self) -> bool:
        """Simple connection test"""
        print("\n🔗 Testing API connection...\n")
        result = self.get_organisations(size=1)
        return result is not None

# ────────────────────────────────────────────────
# Example Usage
if __name__ == "__main__":
    print("\n" + "="*60)
    print("WebCRM API Tester")
    print("="*60)
    print(f"Python: {sys.version.split()[0]}")
    print(f"Requests: {requests.__version__}")
    print(f"Base URL: {BASE_URL}\n")
    
    # Initialize client
    client = WebCRMClient(BASE_URL, TOKEN, debug=True)
    
    # Test 1: Connection test
    # ─────────────────────────────────────────────
    print("\n" + "─"*60)
    print("Test 1: Connection Test")
    print("─"*60)
    if client.test_connection():
        print("✅ Connection successful!\n")
    else:
        print("❌ Connection failed!\n")
        sys.exit(1)
    
    # Test 2: Fetch organisations
    # ─────────────────────────────────────────────
    print("\n" + "─"*60)
    print("Test 2: Fetch Organisations")
    print("─"*60)
    organisations = client.get_organisations(page=1, size=5)
    
    # Test 3: Fetch opportunities
    # ─────────────────────────────────────────────
    print("\n" + "─"*60)
    print("Test 3: Fetch Opportunities")
    print("─"*60)
    opportunities = client.get_opportunities(page=1, size=5)
    
    # Test 4: Fetch specific opportunity (ID 168180 from example file)
    # ─────────────────────────────────────────────
    print("\n" + "─"*60)
    print("Test 4: Fetch Specific Opportunity (ID: 168180)")
    print("─"*60)
    opportunity = client.get_opportunity_by_id("168180")
    
    # Test 5: Fetch persons
    # ─────────────────────────────────────────────
    print("\n" + "─"*60)
    print("Test 5: Fetch Persons")
    print("─"*60)
    persons = client.get_persons(page=1, size=5)
    
    # ─────────────────────────────────────────────
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)
    print("\n💡 NEXT STEPS:")
    print("   - Modify the tests above to match your use case")
    print("   - Add more endpoints as needed")
    print("   - Use this as a test/debugging tool like Postman")
    print("\n")