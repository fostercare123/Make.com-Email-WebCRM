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
load_dotenv(override=True)

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

# ========================================================
# API Client Class
# ========================================================
class WebCRMClient:
    """
    Simple WebCRM API client for testing endpoints.
    
    This client handles WebCRM's 2-step authentication automatically:
    - You provide an authCode (from WebCRM Settings → API)
    - The client exchanges it for an AccessToken behind the scenes
    - You just call methods like get_organisations() and it works!
    
    Example:
        client = WebCRMClient(
            "https://api.webcrm.com", 
            "your-auth-code-here",
            debug=True  # Shows detailed request/response info
        )
        companies = client.get_organisations(page=1, size=20)
    
    All methods automatically handle authentication - you never need to
    think about access tokens manually!
    """
    
    def __init__(self, base_url: str, token: str, debug: bool = True):
        """
        Initialize the WebCRM client.
        
        Args:
            base_url: WebCRM API base URL (e.g., "https://api.webcrm.com")
            token: Your authCode from WebCRM Settings → API
            debug: If True, prints detailed request/response information
        """
        self.base_url = base_url.rstrip("/")
        self.token = token.strip()
        self.debug = debug
        self.headers = {
            "Authorization": f"Bearer {self.token}",  # Replaced dynamically per request
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
    
    def _get_access_token(self) -> Optional[str]:
        """
        Get access token from WebCRM API using the authCode.
        
        WebCRM uses 2-step authentication:
        1. You generate an authCode (API token) in WebCRM Settings → API
        2. This method exchanges the authCode for a temporary AccessToken
        3. The AccessToken is used as a Bearer token for actual API calls
        
        AccessTokens expire after 3600 seconds (1 hour), so we get a fresh
        one for each API request to ensure we never hit expiration.
        
        Returns:
            str: The AccessToken to use for API calls, or None if failed
        """
        try:
            url = f"{self.base_url}/Auth/ApiLogin"
            if self.debug:
                print(f"\n  🔑 Exchanging authCode for AccessToken (Step 1/2)")
            
            # POST the authCode to get an AccessToken
            response = requests.post(url, data={"authCode": self.token}, timeout=15)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("AccessToken")
                if access_token:
                    self._print_debug("Auth", "✅ AccessToken obtained (valid for 1 hour)")
                    return access_token
                else:
                    print(f"❌ No AccessToken in response: {token_data}")
                    return None
            else:
                print(f"❌ Auth failed with status {response.status_code}: {response.text}")
                print(f"   💡 Check your authCode in .env file")
                return None
        except Exception as e:
            print(f"❌ Failed to get access token: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make an HTTP request to the WebCRM API with automatic authentication.
        
        This is the core method that:
        1. Gets a fresh AccessToken from WebCRM (via _get_access_token)
        2. Makes the actual API call with the AccessToken as Bearer token
        3. Returns the JSON response or None if failed
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (e.g., "/Organisations")
            data: Request body for POST/PUT (optional)
            params: URL query parameters (optional)
            
        Returns:
            dict: JSON response data, or None if request failed
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            self._print_request(method, url)
            
            # Step 1: Get fresh access token (automatically handles authCode exchange)
            access_token = self._get_access_token()
            if not access_token:
                print("❌ Failed to obtain access token")
                return None
            
            # Step 2: Use the AccessToken for the actual API call
            headers = self.headers.copy()
            headers["Authorization"] = f"Bearer {access_token}"
            
            if self.debug:
                print(f"  🔑 Using AccessToken for {method} request (Step 2/2)")
            
            # Make the HTTP request
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=15)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=15)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=15)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=15)
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
    
    # ========================================================
    # API Methods - Organisations (Companies)
    # ========================================================
    
    def get_organisations(self, page: int = 1, size: int = 20) -> Optional[list]:
        """
        Fetch a list of organisations (companies) from WebCRM.
        
        Args:
            page: Page number (1-based, default: 1)
            size: Number of results per page (default: 20, max: 250)
            
        Returns:
            list: List of organisation dictionaries, or None if failed
            
        Example:
            companies = client.get_organisations(page=1, size=10)
            for company in companies:
                print(f"{company['OrganisationId']}: {company['OrganisationName']}")
        """
        result = self._make_request("GET", "/Organisations", params={"page": page, "size": size})
        if result:
            print(f"✅ Found {len(result)} organisations")
            if result:
                self._print_debug("Sample", f"Name: {result[0].get('OrganisationName', 'N/A')}")
        return result
    
    def get_organisation_by_id(self, org_id: str) -> Optional[Dict]:
        """
        Fetch a single organisation by its ID.
        
        Args:
            org_id: Organisation ID (as string)
            
        Returns:
            dict: Organisation data, or None if not found
            
        Example:
            company = client.get_organisation_by_id("2")
            print(f"Company: {company['OrganisationName']}")
        """
        result = self._make_request("GET", f"/Organisations/{org_id}")
        if result:
            print(f"✅ Organisation retrieved")
            self._print_debug("Name", result.get("OrganisationName", "N/A"))
        return result
    
    # ========================================================
    # API Methods - Opportunities (Sales/Deals)
    # ========================================================
    
    def get_opportunities(self, page: int = 1, size: int = 20) -> Optional[list]:
        """
        Fetch a list of opportunities (sales/deals) from WebCRM.
        
        Args:
            page: Page number (1-based, default: 1)
            size: Number of results per page (default: 20)
            
        Returns:
            list: List of opportunity dictionaries, or None if failed
            
        Example:
            deals = client.get_opportunities(page=1, size=10)
            for deal in deals:
                print(f"{deal['OpportunityId']}: {deal['Name']} - ${deal.get('Value', 0)}")
        """
        result = self._make_request("GET", "/Opportunities", params={"page": page, "size": size})
        if result:
            print(f"✅ Found {len(result)} opportunities")
        return result
    
    def get_opportunity_by_id(self, opp_id: str) -> Optional[Dict]:
        """
        Fetch a single opportunity by its ID.
        
        Args:
            opp_id: Opportunity ID (as string)
            
        Returns:
            dict: Opportunity data, or None if not found
            
        Example:
            deal = client.get_opportunity_by_id("168180")
            print(f"Deal: {deal['Name']}, Value: {deal.get('Value', 0)}")
        """
        result = self._make_request("GET", f"/Opportunities/{opp_id}")
        if result:
            print(f"✅ Opportunity retrieved")
            self._print_debug("Title", result.get("Name", "N/A"))
        return result
    
    
    # ========================================================
    # API Methods - Persons (Contacts)
    # ========================================================
    
    def get_persons(self, org_id: Optional[str] = None, page: int = 1, size: int = 20) -> Optional[list]:
        """
        Fetch a list of persons (contacts) from WebCRM.
        
        Args:
            org_id: Optional organisation ID to filter by (default: None = all persons)
            page: Page number (1-based, default: 1)
            size: Number of results per page (default: 20)
            
        Returns:
            list: List of person dictionaries, or None if failed
            
        Example:
            # Get all persons
            all_contacts = client.get_persons(page=1, size=20)
            
            # Get persons in a specific company
            company_contacts = client.get_persons(org_id="2", page=1, size=20)
            for person in company_contacts:
                print(f"{person['PersonFirstName']} {person['PersonLastName']}")
        """
        endpoint = f"/Organisations/{org_id}/Persons" if org_id else "/Persons"
        result = self._make_request("GET", endpoint, params={"page": page, "size": size})
        if result:
            print(f"✅ Found {len(result)} persons")
        return result
    
    def create_person(self, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create a new person (contact) in WebCRM.
        
        Args:
            data: Dictionary containing person data
                Required fields: FirstName, LastName
                Optional: Email, Phone, OrganisationId, etc.
                
        Returns:
            dict: Created person data, or None if failed
            
        Example:
            new_person = client.create_person({
                "FirstName": "John",
                "LastName": "Doe",
                "Email": "john.doe@example.com",
                "Phone": "+45 12 34 56 78",
                "OrganisationId": "2"
            })
            print(f"Created person ID: {new_person['PersonId']}")
        """
        result = self._make_request("POST", "/Persons", data=data)
        if result:
            print(f"✅ Person created")
        return result
    
    # ========================================================
    # Utility Methods
    # ========================================================
    
    def test_connection(self) -> bool:
        """
        Simple connection test to verify API access.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Example:
            if client.test_connection():
                print("Ready to use WebCRM API!")
        """
        print("\n🔗 Testing API connection...\n")
        result = self.get_organisations(size=1)
        return result is not None

# ========================================================
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
    # -------------------------------------------------
    print("\n" + "-"*60)
    print("Test 1: Connection Test")
    print("-"*60)
    if client.test_connection():
        print("✅ Connection successful!\n")
    else:
        print("❌ Connection failed!\n")
        sys.exit(1)
    
    # Test 2: Fetch organisations
    # -------------------------------------------------
    print("\n" + "-"*60)
    print("Test 2: Fetch Organisations")
    print("─"*60)
    organisations = client.get_organisations(page=1, size=5)
    
    # Test 3: Fetch opportunities
    # -------------------------------------------------
    print("\n" + "-"*60)
    print("Test 3: Fetch Opportunities")
    print("─"*60)
    opportunities = client.get_opportunities(page=1, size=5)
    
    # Test 4: Fetch specific opportunity (ID 168180 from example file)
    # -------------------------------------------------
    print("\n" + "-"*60)
    print("Test 4: Fetch Specific Opportunity (ID: 168180)")
    print("─"*60)
    opportunity = client.get_opportunity_by_id("168180")
    
    # Test 5: Fetch persons
    # -------------------------------------------------
    print("\n" + "-"*60)
    print("Test 5: Fetch Persons")
    print("─"*60)
    persons = client.get_persons(page=1, size=5)
    
    # -------------------------------------------------
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)
    print("\n💡 NEXT STEPS:")
    print("   - Modify the tests above to match your use case")
    print("   - Add more endpoints as needed")
    print("   - Use this as a test/debugging tool like Postman")
    print("\n")