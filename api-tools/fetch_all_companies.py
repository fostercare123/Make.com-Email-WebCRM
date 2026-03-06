"""
fetch_all_companies.py - Fetch ALL Companies from WebCRM

This script fetches ALL organisations (companies) from WebCRM,
automatically handling pagination when there are more than 250 companies.

Usage:
    python fetch_all_companies.py
"""

import requests
from dotenv import load_dotenv
import os
import sys
from typing import List, Dict, Optional

# Load environment variables
load_dotenv(override=True)

BASE_URL = os.getenv("WEBCRM_BASE_URL", "").strip()
TOKEN = os.getenv("WEBCRM_TOKEN", "").strip()

# Validate configuration
if not BASE_URL or not TOKEN:
    print("❌ ERROR: Missing WEBCRM_BASE_URL or WEBCRM_TOKEN in .env file")
    sys.exit(1)


class CompanyFetcher:
    """Fetches all companies from WebCRM with automatic pagination"""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token.strip()
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.access_token = None  # Cache the access token
        self.token_obtained_at = 0  # Track when we got the token
    
    def _get_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        Exchange authCode for AccessToken (with caching).
        Access tokens are valid for 1 hour, so we reuse them.
        """
        import time
        
        # Reuse cached token if it's less than 50 minutes old (safe margin)
        if not force_refresh and self.access_token:
            age_seconds = time.time() - self.token_obtained_at
            if age_seconds < 3000:  # 50 minutes
                return self.access_token
        
        try:
            url = f"{self.base_url}/Auth/ApiLogin"
            response = requests.post(url, data={"authCode": self.token}, timeout=30)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("AccessToken")
                self.token_obtained_at = time.time()
                return self.access_token
            else:
                print(f"❌ Auth failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Failed to get access token: {str(e)}")
            return None
    
    def _fetch_page(self, page: int, size: int = 250, max_retries: int = 3) -> Optional[List[Dict]]:
        """Fetch a single page of organisations with retry logic"""
        import time
        
        for attempt in range(max_retries):
            try:
                # Get access token (will reuse cached one if still valid)
                access_token = self._get_access_token()
                if not access_token:
                    return None
                
                headers = self.headers.copy()
                headers["Authorization"] = f"Bearer {access_token}"
                
                url = f"{self.base_url}/Organisations"
                params = {"page": page, "size": size}
                
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    # Token expired, refresh and retry
                    print(f"   Token expired, refreshing...")
                    self._get_access_token(force_refresh=True)
                    continue
                else:
                    print(f"❌ Request failed: {response.status_code}")
                    return None
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"   Timeout, retrying (attempt {attempt + 2}/{max_retries})...")
                    time.sleep(2)
                else:
                    print(f"❌ Timeout after {max_retries} attempts")
                    return None
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"   Error: {str(e)}, retrying...")
                    time.sleep(2)
                else:
                    print(f"❌ Error after {max_retries} attempts: {str(e)}")
                    return None
        
        return None
    
    def fetch_all_companies(self) -> List[Dict]:
        """
        Fetch ALL companies from WebCRM with automatic pagination.
        
        Returns:
            List of all company dictionaries
        """
        all_companies = []
        page = 1
        page_size = 250  # Maximum allowed per page
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        print(f"🔍 Fetching all companies from WebCRM...")
        print(f"📄 Page size: {page_size} companies per page")
        print(f"🔄 Using cached access token (valid for 1 hour)\n")
        
        while True:
            print(f"   Page {page:3d}...", end=" ", flush=True)
            
            companies = self._fetch_page(page, page_size)
            
            if companies is None:
                print("❌ Failed!")
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    print(f"\n⚠️  Stopping after {consecutive_failures} consecutive failures")
                    break
                # Skip this page and try the next one
                page += 1
                continue
            
            # Reset failure counter on success
            consecutive_failures = 0
            
            if len(companies) == 0:
                print("✅ Empty page (reached the end)")
                break
            
            all_companies.extend(companies)
            print(f"✅ {len(companies):3d} companies (total: {len(all_companies):,})")
            
            # If we got fewer companies than the page size, we've reached the end
            if len(companies) < page_size:
                print(f"\n✅ Reached the last page (page {page} returned only {len(companies)} companies)")
                break
            
            page += 1
        
        return all_companies
    
    def display_companies(self, companies: List[Dict], show_details: bool = False):
        """
        Display the fetched companies in a nice format.
        
        Args:
            companies: List of company dictionaries
            show_details: If True, show more details for each company
        """
        print("\n" + "="*70)
        print(f"📋 ALL COMPANIES ({len(companies)} total)")
        print("="*70)
        
        if not companies:
            print("   No companies found.")
            return
        
        for i, company in enumerate(companies, 1):
            org_id = company.get('OrganisationId', 'N/A')
            org_name = company.get('OrganisationName', 'N/A')
            
            if show_details:
                # Show more details
                phone = company.get('Phone', 'N/A')
                email = company.get('Email', 'N/A')
                city = company.get('City', 'N/A')
                
                print(f"\n{i}. {org_name}")
                print(f"   ID: {org_id}")
                print(f"   Phone: {phone}")
                print(f"   Email: {email}")
                print(f"   City: {city}")
            else:
                # Simple list
                print(f"{i:4d}. {org_name:50s} (ID: {org_id})")
        
        print("\n" + "="*70)
    
    def save_to_file(self, companies: List[Dict], filename: str = "all_companies.json"):
        """Save companies to a JSON file"""
        import json
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(companies, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Saved {len(companies)} companies to {filename}")
        except Exception as e:
            print(f"❌ Failed to save file: {str(e)}")


# ========================================================
# Main Execution
# ========================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("WebCRM - Fetch ALL Companies")
    print("="*70)
    print(f"Base URL: {BASE_URL}\n")
    
    # Initialize fetcher
    fetcher = CompanyFetcher(BASE_URL, TOKEN)
    
    # Fetch all companies
    all_companies = fetcher.fetch_all_companies()
    
    # Display results
    if all_companies:
        print(f"\n✅ Successfully fetched {len(all_companies)} companies!")
        
        # Ask user how to display
        print("\n" + "-"*70)
        print("Display Options:")
        print("  1. Simple list (name + ID)")
        print("  2. Detailed view (includes phone, email, city)")
        print("  3. Save to JSON file and show simple list")
        print("  4. Save to JSON file only (no display)")
        print("-"*70)
        
        choice = input("Choose option (1-4) [default: 1]: ").strip() or "1"
        
        if choice == "1":
            fetcher.display_companies(all_companies, show_details=False)
        elif choice == "2":
            fetcher.display_companies(all_companies, show_details=True)
        elif choice == "3":
            fetcher.save_to_file(all_companies)
            fetcher.display_companies(all_companies, show_details=False)
        elif choice == "4":
            fetcher.save_to_file(all_companies)
        else:
            print("Invalid choice, showing simple list:")
            fetcher.display_companies(all_companies, show_details=False)
        
        print("\n✅ Done!")
    else:
        print("\n❌ No companies fetched. Check your connection and credentials.")
        sys.exit(1)
