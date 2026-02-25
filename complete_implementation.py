"""
Complete working example: Search and update QuotationLine by Uniconta item number
This demonstrates the exact logic needed in Make.com Module 3 and 4
"""

import os
import json
from dotenv import load_dotenv
import requests
from typing import Optional, Tuple

load_dotenv()

class WebCRMClient:
    def __init__(self):
        self.base_url = os.getenv('WEBCRM_BASE_URL', 'https://api.webcrm.com')
        self.auth_code = os.getenv('WEBCRM_TOKEN')
        self.access_token = None
        self.authenticate()
    
    def authenticate(self):
        """Get access token from webCRM"""
        response = requests.post(
            f'{self.base_url}/Auth/ApiLogin',
            data={'authCode': self.auth_code}
        )
        if response.status_code == 200:
            self.access_token = response.json()['AccessToken']
            print("[AUTH] Access token obtained")
        else:
            raise Exception(f"Authentication failed: {response.status_code}")
    
    @property
    def headers(self):
        """Standard headers for all requests"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
    
    def search_quotation_line_by_item(self, item_number: str) -> Optional[dict]:
        """
        Search for a QuotationLine by Uniconta item number
        Item numbers are stored in QuotationLineData4
        
        Args:
            item_number: The Uniconta item number (e.g., "60900100")
            
        Returns:
            Dictionary with QuotationLine data if found, None otherwise
        """
        print(f"\n[SEARCH] Looking for item: {item_number}")
        
        # Get first page of quotation lines (can paginate if needed)
        response = requests.get(
            f'{self.base_url}/QuotationLines?page=1&size=250',
            headers=self.headers,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Failed to fetch quotation lines: {response.status_code}")
            return None
        
        quotation_lines = response.json()
        print(f"[SEARCH] Retrieved {len(quotation_lines)} quotation lines")
        
        # Search for matching item number in QuotationLineData4
        for line in quotation_lines:
            if line.get('QuotationLineData4') == item_number:
                print(f"[FOUND] Matching QuotationLine ID: {line['QuotationLineId']}")
                print(f"  Item: {line.get('QuotationLineData4')}")
                print(f"  Current Price: {line.get('QuotationLinePrice')}")
                print(f"  Current CostPrice: {line.get('QuotationLineCostPrice')}")
                return line
        
        print(f"[NOT FOUND] No QuotationLine with item number: {item_number}")
        return None
    
    def update_quotation_line_price(
        self,
        quotation_line_id: int,
        new_price: float = None,
        new_cost_price: float = None,
        new_quantity: float = None
    ) -> bool:
        """
        Update the price of a QuotationLine
        
        Args:
            quotation_line_id: The ID of the QuotationLine to update
            new_price: New selling price (QuotationLinePrice)
            new_cost_price: New cost price (QuotationLineCostPrice)
            new_quantity: New quantity (QuotationLineQuantity)
            
        Returns:
            True if successful, False otherwise
        """
        print(f"\n[UPDATE] Updating QuotationLine {quotation_line_id}")
        
        # Build update body with only provided fields
        body = {"QuotationLineId": quotation_line_id}
        
        if new_price is not None:
            body['QuotationLinePrice'] = new_price
            print(f"  Setting Price: {new_price}")
        
        if new_cost_price is not None:
            body['QuotationLineCostPrice'] = new_cost_price
            print(f"  Setting CostPrice: {new_cost_price}")
        
        if new_quantity is not None:
            body['QuotationLineQuantity'] = new_quantity
            print(f"  Setting Quantity: {new_quantity}")
        
        # Send update request
        response = requests.put(
            f'{self.base_url}/QuotationLines/{quotation_line_id}',
            headers=self.headers,
            json=body,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"[SUCCESS] QuotationLine {quotation_line_id} updated")
            return True
        else:
            print(f"[ERROR] Update failed: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
    
    def sync_uniconta_price(
        self,
        uniconta_item: str,
        cost_price: float,
        sales_price: float,
        quantity: float = None
    ) -> bool:
        """
        Complete workflow: Find item in webCRM and update its price
        
        This is the full integration matching the Make.com modules
        
        Args:
            uniconta_item: Uniconta item number (e.g., "60900100")
            cost_price: Cost price from Uniconta
            sales_price: Sales price from Uniconta
            quantity: Quantity (optional)
            
        Returns:
            True if sync successful, False otherwise
        """
        print("\n" + "=" * 60)
        print("UNICONTA PRICE SYNC")
        print("=" * 60)
        print(f"Item: {uniconta_item}")
        print(f"Cost Price: {cost_price}")
        print(f"Sales Price: {sales_price}")
        if quantity:
            print(f"Quantity: {quantity}")
        
        # Module 3: Search for matching QuotationLine
        quotation_line = self.search_quotation_line_by_item(uniconta_item)
        if not quotation_line:
            print("[FAILED] Item not found in webCRM")
            return False
        
        # Module 4: Update the QuotationLine
        success = self.update_quotation_line_price(
            quotation_line['QuotationLineId'],
            new_price=sales_price,
            new_cost_price=cost_price,
            new_quantity=quantity
        )
        
        return success


def simulate_uniconta_webhook():
    """
    Simulate receiving a Uniconta webhook with updated prices
    This is what Make.com webhook trigger provides
    """
    # Example payload from Uniconta webhook
    webhook_payload = {
        'Table': 'InvItem',
        'Action': 'update',
        'Item': '61121042',  # The item number to search for
        'Name': 'Example Product',
        'CostPrice': 1500.00,  # Updated cost price
        'PurchasePrice': 1600.00,
        'SalesPrice1': 3050.00,  # Updated selling price
        'Qty': 4.0,
        'Unit': 'Unit'
    }
    return webhook_payload


if __name__ == '__main__':
    try:
        # Initialize client (Module 1: Authentication)
        client = WebCRMClient()
        
        # Simulate Uniconta webhook (what Make.com webhook trigger sends)
        uniconta_data = simulate_uniconta_webhook()
        
        print("\n" + "=" * 60)
        print("SIMULATED UNICONTA WEBHOOK")
        print("=" * 60)
        print(json.dumps(uniconta_data, indent=2))
        
        # Execute sync (Modules 3 & 4)
        success = client.sync_uniconta_price(
            uniconta_item=uniconta_data['Item'],
            cost_price=uniconta_data['CostPrice'],
            sales_price=uniconta_data['SalesPrice1'],
            quantity=uniconta_data['Qty']
        )
        
        if success:
            print("\n[RESULT] Price sync completed successfully!")
            print("Changes are now live in webCRM")
        else:
            print("\n[RESULT] Price sync failed - check error messages above")
            
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")


# Make.com JavaScript equivalent for Module 3 (Search):
"""
This would be your "Find QuotationLine" step in Make.com:

{{http(
  "url": `https://api.webcrm.com/QuotationLines?page=1&size=250`,
  "method": "GET",
  "headers": {
    "Authorization": `Bearer {{1.AccessToken}}`,
    "Accept": "application/json"
  }
)
.map(item => if(item.QuotationLineData4 = {{unicontaItem}}; item))
.filter(i => i != null)
[0]}}
"""

# Make.com JavaScript equivalent for Module 4 (Update):
"""
This would be your "Update Price" step in Make.com:

{{http(
  "url": `https://api.webcrm.com/QuotationLines/{{3.QuotationLineId}}`,
  "method": "PUT",
  "headers": {
    "Authorization": `Bearer {{1.AccessToken}}`,
    "Content-Type": "application/json"
  },
  "data": {
    "QuotationLineId": {{3.QuotationLineId}},
    "QuotationLinePrice": {{unicontaSalesPrice}},
    "QuotationLineCostPrice": {{unicontaCostPrice}},
    "QuotationLineQuantity": {{unicontaQty}}
  }
)}}
"""
