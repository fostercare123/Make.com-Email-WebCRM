# Make.com Scenario Analysis: Uniconta → webCRM Price Sync

## 📊 Current Setup Overview

Your scenario has 4 modules that sync Uniconta product prices to webCRM:

```
Webhook Trigger → Get Access Token → Search Items → Update Price
   (Module 2)       (Module 11)       (Module 6)     (Module 13)
```

---

## ✅ What's Working Correctly

### Module 2: Uniconta Product Update Trigger ✓
```
Type: Webhook
Endpoint: Custom webhook listening for Uniconta updates
```
**Status:** ✅ Correctly configured
- Receives POST data from Uniconta InvItem table
- Captures: `Item` (item number), `SalesPrice1`, `CostPrice`

### Module 11: Get webCRM Access Token ✓
```
POST https://api.webcrm.com/Auth/ApiLogin
Body: authCode=17a6ee13-aeec-4413-8736-2fee9df2c113
```
**Status:** ✅ Correctly configured
- Proper endpoint
- Correct Content-Type: `application/x-www-form-urlencoded`
- Returns: `{{11.data.AccessToken}}`

### Module 13: Update Price ✓ (with caveat)
```
PUT https://api.webcrm.com/QuotationLines/{{6.data[].QuotationLineId}}
Body:
{
  "QuotationLineId": {{6.data[].QuotationLineId}},
  "QuotationLinePrice": {{2.SalesPrice1}},
  "QuotationLineCostPrice": {{2.CostPrice}}
}
```
**Status:** ⚠️ **Mostly correct** but see critical issue below

---

## 🚨 CRITICAL ISSUE: Missing Item Filter

### The Problem

**Module 6** retrieves ALL 250 quotation lines:
```
GET /QuotationLines?page=1&size=250
```

But **Module 13** uses `{{6.data[].QuotationLineId}}` which will:
- ❌ Try to update **ALL 250 lines** with the same price
- ❌ NOT match the Uniconta item number to the correct webCRM line

### What's Missing

You need to **filter the array** to find the matching item BEFORE updating:

```
QuotationLines Array → Find where QuotationLineData4 == {{2.Item}} → Update ONLY that line
```

---

## 🔧 Required Fix: Add Iterator/Filter Module

### Option 1: Use Array Iterator (Recommended)

**Add between Module 6 and Module 13:**

1. **Add Iterator Module**
   - Module: `Array Iterator`
   - Array: `{{6.data}}`
   - This will process each line one at a time

2. **Add Filter Module** (after Iterator)
   - Condition: `{{6.QuotationLineData4}}` **equals** `{{2.Item}}`
   - This ensures only matching lines proceed to update

3. **Update Module 13:**
   - Change: `{{6.data[].QuotationLineId}}` 
   - To: `{{6.QuotationLineId}}` (singular, from iterator)

### Option 2: Use Array Functions (Advanced)

Add a **Set Variable** module after Module 6:

```
Name: MatchingLineId
Value: {{first(map(6.data; "QuotationLineId"; "QuotationLineData4"; 2.Item))}}
```

Then in Module 13:
```
URL: /QuotationLines/{{MatchingLineId}}
Body QuotationLineId: {{MatchingLineId}}
```

---

## 🔒 Security Recommendation

### URGENT: Remove Hardcoded authCode

Your authCode is visible in the blueprint:
```
authCode=17a6ee13-aeec-4413-8736-2fee9df2c113
```

**Fix:**
1. Go to Module 11 settings
2. Replace hardcoded value with a **Variable** or **Datastore** value
3. Store the authCode in Make.com's **Data Store** or use **Environment Variables**

---

## 🎯 How Your Scenario Works (Step-by-Step)

### 1. Uniconta Sends Webhook
When someone updates a product in Uniconta:
```json
{
  "Item": "60900100",
  "SalesPrice1": 99.99,
  "CostPrice": 49.30
}
```

### 2. Make.com Gets Access Token
Exchanges your authCode for a temporary AccessToken (valid 1 hour):
```json
{
  "AccessToken": "abc123...",
  "ExpiresIn": 3600
}
```

### 3. Make.com Searches QuotationLines
Retrieves up to 250 quotation lines from webCRM:
```json
[
  {
    "QuotationLineId": 12,
    "QuotationLineData4": "61121042",
    "QuotationLinePrice": 2895.00
  },
  {
    "QuotationLineId": 15,
    "QuotationLineData4": "60900100",  ← MATCH!
    "QuotationLinePrice": 89.50
  },
  ...
]
```

### 4. Make.com Updates the Matching Line
**⚠️ Currently broken** - needs filter (see fix above)

**After fix:**
```
PUT /QuotationLines/15
{
  "QuotationLineId": 15,
  "QuotationLinePrice": 99.99,
  "QuotationLineCostPrice": 49.30
}
```

---

## 📈 Improvements & Optimizations

### 1. Add Error Handling

Add **Error Handler** routes for:

**After Module 11 (Auth):**
- If status ≠ 200: Send notification "Auth failed"

**After Module 6 (Search):**
- If data is empty: Send notification "No quotation lines found"

**After Module 13 (Update):**
- If status = 404: Log "Item not in webCRM yet"
- If status = 429: Wait and retry (rate limited)

### 2. Add Logging

Add **Data Store** module after Module 13:
```
Store:
- Timestamp
- Item Number
- Old Price
- New Price
- Status (success/error)
```

### 3. Handle Multiple Matches

If one item number appears in multiple quotation lines:

**Add aggregator** after the iterator to:
- Update all matching lines
- Report how many were updated

### 4. Pagination Handling

If you have >250 quotation lines:

**Option A:** Increase page size (max 250)
**Option B:** Add pagination loop to check all pages
**Option C:** Use webCRM API filter (if available)

### 5. Add Notification

Add **Email** or **Slack** module at the end:
```
"Updated item {{2.Item}} in webCRM
Old price: {{6.QuotationLinePrice}}
New price: {{2.SalesPrice1}}
Difference: {{2.SalesPrice1 - 6.QuotationLinePrice}}"
```

---

## 🚀 Extending to Other Uniconta → webCRM Updates

### Sync Organization/Customer Data

**Webhook:** Uniconta Customer (Debtor) table
**Endpoint:** `PUT /Organisations/{id}`

**Mapping:**
| Uniconta Field | webCRM Field |
|---|---|
| `Account` | OrganisationNumber |
| `Name` | OrganisationName |
| `Address1` | OrganisationAddress |
| `ZipCode` | OrganisationZipCode |
| `City` | OrganisationCity |
| `Country` | OrganisationCountry |
| `Phone` | OrganisationPhone |
| `Email` | OrganisationEmail |
| `Www` | OrganisationWebsite |
| `VatNumber` | OrganisationVatNumber |

### Sync Contact Person Data

**Webhook:** Uniconta Contact table
**Endpoint:** `PUT /Persons/{id}` or `POST /Persons`

**Mapping:**
| Uniconta Field | webCRM Field |
|---|---|
| `FirstName` | PersonFirstName |
| `LastName` | PersonLastName |
| `Email` | PersonEmail |
| `Phone` | PersonPhone |
| `Mobile` | PersonMobile |
| `Account` (link) | OrganisationId |

### Sync Quotation Header

**Webhook:** Uniconta Offer (Quotation) table
**Endpoint:** `PUT /Opportunities/{id}`

**Mapping:**
| Uniconta Field | webCRM Field |
|---|---|
| `OrderNumber` | OpportunityNumber |
| `DeliveryDate` | OpportunityDeliveryDate |
| `Total` | Value |
| `Status` | OpportunityStatus |
| `Account` (link) | OrganisationId |

### Create New Products

**Webhook:** Uniconta InvItem CREATE event
**Endpoint:** `POST /Products`

**Mapping:**
| Uniconta Field | webCRM Field |
|---|---|
| `Item` | ProductNumber |
| `Name` | ProductName |
| `SalesPrice1` | ProductPrice |
| `CostPrice` | ProductCostPrice |
| `StandardVariant` | ProductDescription |
| `Unit` | ProductUnit |

---

## 🏗️ Reference Architecture

### Current Flow (Needs Fix)
```
┌─────────────────┐
│   1. Webhook    │  Uniconta InvItem update
│   (Trigger)     │  → Item: "60900100"
└────────┬────────┘  → SalesPrice1: 99.99
         │            → CostPrice: 49.30
         ↓
┌─────────────────┐
│  2. Get Token   │  POST /Auth/ApiLogin
│  (HTTP)         │  → AccessToken
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  3. Get Lines   │  GET /QuotationLines?size=250
│  (HTTP)         │  → Array of 250 lines
└────────┬────────┘
         │
         │  ⚠️ MISSING: Filter by Item Number
         │
         ↓
┌─────────────────┐
│  4. Update ALL  │  ❌ Updates all 250 lines!
│  (HTTP PUT)     │  Should only update matching line
└─────────────────┘
```

### Fixed Flow (Recommended)
```
┌─────────────────┐
│   1. Webhook    │  Uniconta InvItem update
│   (Trigger)     │  → Item: "60900100"
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  2. Get Token   │  POST /Auth/ApiLogin
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  3. Get Lines   │  GET /QuotationLines?size=250
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  4. Iterator    │  ✓ Loop through each line
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  5. Filter      │  ✓ IF QuotationLineData4 == Item
└────────┬────────┘     THEN continue, ELSE stop
         │
         ↓ (only matching items)
┌─────────────────┐
│  6. Update      │  ✓ Update only matched line(s)
│  (HTTP PUT)     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  7. Log/Notify  │  ✓ Record success
└─────────────────┘
```

---

## 📝 Implementation Checklist

- [ ] **CRITICAL:** Add Iterator module after "Search Items"
- [ ] **CRITICAL:** Add Filter for `QuotationLineData4 == Item`
- [ ] **CRITICAL:** Update Module 13 to use single item ID
- [ ] **SECURITY:** Move authCode to Data Store or variable
- [ ] Add error handler for authentication failure
- [ ] Add error handler for "item not found"
- [ ] Add logging of successful updates
- [ ] Add email/Slack notification (optional)
- [ ] Test with real Uniconta webhook
- [ ] Document what happens when item not found in webCRM

---

## 🧪 Testing Your Fix

1. **Create test webhook payload:**
```json
{
  "Item": "61121042",
  "SalesPrice1": 3000.00,
  "CostPrice": 1200.00
}
```

2. **Manually trigger webhook** in Make.com

3. **Verify:**
   - ✅ Module 11 returns AccessToken
   - ✅ Module 6 returns array of lines
   - ✅ Iterator processes each line
   - ✅ Filter finds ONLY line with `QuotationLineData4 = "61121042"`
   - ✅ Module 13 updates ONLY that line
   - ✅ webCRM shows new price: 3000.00

---

## 📚 Additional Resources

- [MAKE_COM_SOLUTION.md](MAKE_COM_SOLUTION.md) - Original integration guide
- [complete_implementation.py](complete_implementation.py) - Python reference implementation
- [test_webcrm.py](test_webcrm.py) - Test the API directly
- [Make.com Array Iterator Docs](https://www.make.com/en/help/tools/flow-control#iterator-951241)
- [Make.com Filters](https://www.make.com/en/help/scenarios/filters)

---

**Last Updated:** February 26, 2026  
**Scenario Version:** 1.0 (requires fixes noted above)
