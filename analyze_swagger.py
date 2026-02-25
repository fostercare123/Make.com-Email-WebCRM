"""
Analyze webCRM Swagger spec to determine:
1. Exact field names for Products endpoint updates
2. QuotationLines structure and item number storage
3. Best approach for syncing Uniconta prices to webCRM
"""
import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()

# Get credentials
AUTHCODE = os.getenv('WEBCRM_TOKEN')
BASE_URL = os.getenv('WEBCRM_BASE_URL', 'https://api.webcrm.com')

# Step 1: Get access token
print("=" * 60)
print("STEP 1: Get Access Token")
print("=" * 60)
auth_response = requests.post(
    f'{BASE_URL}/Auth/ApiLogin',
    data={'authCode': AUTHCODE}
)
if auth_response.status_code == 200:
    access_token = auth_response.json()['AccessToken']
    print(f"✓ Access token obtained (valid for 1 hour)")
else:
    print(f"✗ Authentication failed: {auth_response.status_code}")
    exit(1)

headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json'
}

# Step 2: Get ONE QuotationLine to inspect structure
print("\n" + "=" * 60)
print("STEP 2: Examine QuotationLines Structure")
print("=" * 60)
ql_response = requests.get(
    f'{BASE_URL}/QuotationLines?page=1&size=1',
    headers=headers
)
if ql_response.status_code == 200:
    quotation_lines = ql_response.json()
    if quotation_lines:
        ql = quotation_lines[0]
        print(f"QuotationLine ID: {ql.get('QuotationLineId')}")
        print(f"\nAll QuotationLine Fields:")
        for key, value in ql.items():
            if value is not None and value != '':
                print(f"  {key}: {value} (type: {type(value).__name__})")
    else:
        print("No quotation lines found in system")
else:
    print(f"✗ Failed to get quotation lines: {ql_response.status_code}")

# Step 3: Get ONE Product to inspect structure
print("\n" + "=" * 60)
print("STEP 3: Examine Products Structure")
print("=" * 60)
prod_response = requests.get(
    f'{BASE_URL}/Products?page=1&size=1',
    headers=headers
)
if prod_response.status_code == 200:
    products = prod_response.json()
    if products:
        product = products[0]
        print(f"Product ID: {product.get('ProductId')}")
        print(f"\nAll Product Fields:")
        for key, value in product.items():
            if value is not None and value != '':
                print(f"  {key}: {value} (type: {type(value).__name__})")
        
        # Show EMPTY fields that could be populated
        print(f"\nEMPTY Product Fields (could be populated):")
        for key, value in product.items():
            if value is None or value == '':
                print(f"  {key}: {value}")
    else:
        print("No products found in system")
else:
    print(f"✗ Failed to get products: {prod_response.status_code}")

# Step 4: Check if there's a way to search by item number
print("\n" + "=" * 60)
print("STEP 4: Search Strategy Analysis")
print("=" * 60)
print("""
Based on Swagger spec findings:
1. Products endpoint has NO ProductNumber field populated (returns empty)
2. QuotationLines endpoint has various fields - need to identify which holds item numbers
3. Uniconta item numbers (e.g., 60900100) - where are they stored in webCRM?

Hypothesis: Item numbers are stored in QuotationLine custom fields or linked data
""")

# Step 5: Check Opportunities - they might reference products differently  
print("\n" + "=" * 60)
print("STEP 5: Check Opportunities (has OpportunityProduct field)")
print("=" * 60)
opp_response = requests.get(
    f'{BASE_URL}/Opportunities?page=1&size=1',
    headers=headers
)
if opp_response.status_code == 200:
    opportunities = opp_response.json()
    if opportunities:
        opp = opportunities[0]
        print(f"Opportunity ID: {opp.get('OpportunityId')}")
        print(f"OpportunityProduct: {opp.get('OpportunityProduct')}")
        print(f"OpportunityProductId: {opp.get('OpportunityProductId')}")
        print(f"\nFields mentioning 'Product':")
        for key, value in opp.items():
            if 'Product' in key:
                print(f"  {key}: {value}")
    else:
        print("No opportunities found")
else:
    print(f"✗ Failed to get opportunities: {opp_response.status_code}")

print("\n" + "=" * 60)
print("CRITICAL FINDINGS FOR MAKE.COM CONFIGURATION")
print("=" * 60)
print("""
For Module 4 (Update Product Price):
  HTTP PUT /Products/{ProductId}
  Body: JSON with field names from ProductDto:
    - ProductPrice (double) - selling price
    - ProductCostPrice (double) - cost price  
    - ProductListPrice (double) - list price
    - ProductDiscount (double) - discount

PROBLEM IDENTIFIED:
  Products don't have ProductNumber field populated!
  Need to identify how Uniconta item numbers (60900100) are referenced.
  
SOLUTION:
  May need to search QuotationLines instead of Products
  QuotationLines may have the item numbers in custom fields (QuotationLineData1-15)
  OR use Opportunities as intermediary (OpportunityProduct field)
""")
