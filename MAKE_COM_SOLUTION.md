# Make.com Automation: Sync Uniconta Prices to webCRM

## CRITICAL DISCOVERY
**Uniconta item numbers (like 60900100) are stored in `QuotationLineData4` in webCRM, NOT in the Products endpoint.**

---

## End-to-End Solution

### Module 1: Get Access Token (✓ ALREADY CONFIGURED)
```
POST https://api.webcrm.com/Auth/ApiLogin
Body: application/x-www-form-urlencoded
  authCode: [your WEBCRM_TOKEN]
Returns: AccessToken (valid 1 hour)
```

### Module 2: Get All Products (✓ ALREADY CONFIGURED)  
```
GET https://api.webcrm.com/Products?page=1&size=250
Headers: Bearer {{AccessToken}}
Returns: Product list (for reference, NOT used for item matching)
```

### **MODULE 3: Search QuotationLines for Item Number** ⭐ NEW
This is the key module that finds the matching line item by Uniconta item number.

```
URL: GET https://api.webcrm.com/QuotationLines?page=1&size=250

Headers:
  Authorization: Bearer {{AccessToken}}
  Accept: application/json

Expected Response:
- Array of QuotationLine objects
- Each line has QuotationLineData4 containing the item number
- Example: QuotationLineData4 = "61121042" (matches Uniconta item)

Field Reference:
  QuotationLineId          → ID needed for update (Module 4)
  QuotationLineData4       → ITEM NUMBER (search by this!)
  QuotationLinePrice       → Current selling price
  QuotationLineCostPrice   → Current cost price
  QuotationLineQuantity    → Quantity
  QuotationLineComment     → Comments
```

### **MODULE 4: Update Matching QuotationLine Price** ⭐ NEW
Once you find the matching QuotationLine by item number, update its price.

```
URL: PUT https://api.webcrm.com/QuotationLines/{{QuotationLineId}}

Headers:
  Authorization: Bearer {{AccessToken}}
  Content-Type: application/json

Body (JSON):
{
  "QuotationLineId": {{QuotationLineId from Module 3}},
  "QuotationLinePrice": {{From Uniconta SalesPrice1}},
  "QuotationLineCostPrice": {{From Uniconta CostPrice}},
  "QuotationLineQuantity": {{From Uniconta Qty (if available)}}
}

Response: 
  200 OK - Success
  401 - Unauthorized (check token expiry)
  404 - QuotationLine not found
```

---

## Field Mapping: Uniconta → webCRM

| Uniconta Field | Uniconta Example | webCRM Endpoint | webCRM Field | webCRM Example |
|---|---|---|---|---|
| **Item** (item number) | 60900100 | QuotationLines | QuotationLineData4 | 61121042 |
| **CostPrice** | 49.30 | QuotationLines/{id} | QuotationLineCostPrice | 1178.63 |
| **PurchasePrice** | 53.00 | QuotationLines/{id} | QuotationLineCostPrice | (same as above) |
| **SalesPrice1** | 99.99 | QuotationLines/{id} | QuotationLinePrice | 2895.00 |
| **Name** | Product Name | QuotationLines | QuotationLineData2 | (display field) |
| **Qty** | 10 | QuotationLines/{id} | QuotationLineQuantity | 4.0 |

---

## Make.com Configuration Steps

### Step 1: Add Filter Module (optional but recommended)
After Module 2, add a **Router** or **Filter**:
```
Condition: 
  IF {{3.QuotationLineData4}} EQUALS {{1.Item}}
  THEN continue to Module 4
  ELSE log error or end
```

### Step 2: Add Search Module (Module 3)
```
Search through all quotation lines returned from GET /QuotationLines
For each line, check if QuotationLineData4 equals the Uniconta Item number
Store the matching QuotationLineId and current prices
```

Implementation options:
- **Option A (Recommended)**: Use Make.com's Array functions to find first match
  ```
  {{first(map(1.QuotationLines; if(item.QuotationLineData4 = {{unicontaItem}}; item)))}}
  ```
- **Option B (Manual)**: Use a loop to iterate through lines and find match
- **Option C (Conditional)**: POST query request with filter parameter (if webCRM supports it)

### Step 3: Add Update Module (Module 4)
```
HTTP Method: PUT
URL: https://api.webcrm.com/QuotationLines/{{3.QuotationLineId}}
Headers: 
  Authorization: Bearer {{1.AccessToken}}
  Content-Type: application/json
Body:
{
  "QuotationLineId": {{3.QuotationLineId}},
  "QuotationLineCostPrice": {{webhookPayload.CostPrice}},
  "QuotationLinePrice": {{webhookPayload.SalesPrice1}},
  "QuotationLineQuantity": {{webhookPayload.Qty}}
}
```

### Step 4: Error Handling
Add error routes for:
- No matching QuotationLine found (item not in webCRM yet)
- 401 Unauthorized (token expired/invalid)
- 429 Too Many Requests (rate limited)
- 404 Not Found (QuotationLineId is invalid)

---

## Actual Quotation Line Data Examples

From webCRM system:

| QL ID | Data4 (Item) | Data2 | Data3 | Price | CostPrice |
|---|---|---|---|---|---|
| 12 | 61121042 | SD | 1000Kg | 2895.00 | 1178.63 |
| 13 | 69210001 | MCE2010 | Vejececelle | TBD | TBD |
| 14 | 69101200 | MCE9601 | Terminal | TBD | TBD |
| 15 | 66911003 | Montageset | - | TBD | TBD |
| 16 | 10000002 | Special rabat | - | TBD | TBD |

**Pattern confirmed**: QuotationLineData4 = Product Item Number

---

## Advanced Notes

### Why NOT Products endpoint?
- ProductNumber field is empty/null in webCRM
- Products don't have direct item numbers
- QuotationLines are where actual line items with prices are managed
- This matches webCRM's quotation-centric architecture

### Alternative for future: Products endpoint
If you want to update base Products instead:
```
PUT https://api.webcrm.com/Products/{{ProductId}}
Body:
{
  "ProductPrice": {{new_price}},
  "ProductCostPrice": {{new_cost}},
  "ProductListPrice": {{suggested_list}},
  "ProductCustom1": "60900100"  // Store Uniconta item number here
}
```

### Quotation Line Endpoints Available
```
GET    /QuotationLines              - List all lines
GET    /QuotationLines/{id}         - Get specific line
GET    /Opportunities/{id}/QuotationLines  - Lines for opportunity
GET    /Deliveries/{id}/QuotationLines     - Lines for delivery
PUT    /QuotationLines/{id}         - Update line
POST   /QuotationLines              - Create new line
PATCH  /QuotationLines              - Bulk update
DELETE /QuotationLines/{id}         - Delete line
```

---

## Testing Your Configuration

### Test 1: Search for specific item
```
GET https://api.webcrm.com/QuotationLines?page=1&size=250
Authorization: Bearer {{token}}

Look for: QuotationLineData4 = "61121042"
Expected: Should find QuotationLine ID 12
```

### Test 2: Update that line
```
PUT https://api.webcrm.com/QuotationLines/12
Authorization: Bearer {{token}}

Body:
{
  "QuotationLineId": 12,
  "QuotationLineCostPrice": 1500.00,
  "QuotationLinePrice": 3000.00
}

Expected: 200 OK
```

### Test 3: Verify in webCRM UI
Check QuotationLine 12 in webCRM - prices should update immediately

---

## Complete Module Flow

```
UNICONTA WEBHOOK (InvItem update)
    ↓
    Item: "60900100"
    CostPrice: 49.30
    SalesPrice1: 99.99
    ↓
MODULE 3: Search QuotationLines
    GET /QuotationLines?page=1&size=250
    Find: QuotationLineData4 = "60900100"
    Extract: QuotationLineId = 12
    ↓
MODULE 4: Update Price
    PUT /QuotationLines/12
    Set QuotationLineCostPrice = 49.30
    Set QuotationLinePrice = 99.99
    ↓
WEBCRM UPDATED
    QuotationLine 12 now has new prices
    Updated = {{timestamp}}
```

---

## Glossary

| Term | Definition |
|---|---|
| **QuotationLine** | A single product line item in a quotation/opportunity |
| **QuotationLineData4** | Custom field storing the item number (Uniconta reference) |
| **QuotationLinePrice** | Selling/quote price shown to customer |
| **QuotationLineCostPrice** | Internal cost price (margin calculation) |
| **Opportunity** | A sales opportunity - contains multiple QuotationLines |
| **Item Number** | Unique identifier from Uniconta (e.g., 60900100) |
| **AccessToken** | Bearer token for API authentication (1 hour validity) |

---

## Next Steps

1. ✓ Add Module 3: GET /QuotationLines with search logic
2. ✓ Add Module 4: PUT /QuotationLines/{id} with new prices
3. Add error handling for missing items
4. Test with actual Uniconta webhook payload
5. Monitor token expiry and refresh if needed (every 59 minutes)
