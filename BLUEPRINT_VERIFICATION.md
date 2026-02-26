# Blueprint Analysis: Integration Webhooks (Updated)

## ✅ What's Correct

### Module 2: Webhook Trigger ✓
- Correctly configured to listen for Uniconta updates
- Receives Item, SalesPrice1, CostPrice

### Module 6: Search Items ✓
- Correctly fetches all QuotationLines
- Proper authorization header with AccessToken
- Size 250 is good

### Module 15: Iterator/BasicFeeder ✓
- **Excellent!** You used `builtin:BasicFeeder` (Make.com's iterator)
- Array correctly set to: `{{6.data}}`
- This will process each line one at a time

### Module 13: Update Price URL ✓
- **Perfect!** URL now uses: `https://api.webcrm.com/QuotationLines/{{15.QuotationLineId}}`
- Body correctly references: `{{15.QuotationLineId}}` (from iterator, not array)
- This will update only the matching line!

---

## ⚠️ Things to Verify

### 1. Module 13 Filter Condition
Your blueprint shows:
```json
"filter": {
    "name": "Filter",
    "conditions": [
        [
            {/* Lines 734-737 omitted */}
        ]
    ]
}
```

**Make sure the filter condition is:**
```
{{15.QuotationLineData4}} equals {{2.Item}}
```

If not, you need to add/update it. This is the critical filter that ensures you only update matching items!

**To check:**
1. Open Module 13 in Make.com
2. Look for the **Filter** section (should be just before the URL field)
3. The condition should show: `QuotationLineData4 equals Item`

### 2. Module 11 AuthCode - Still Hardcoded
```json
"urlEncodedBodyContent": [
    {
        "name": "authCode",
        "value": "17a6ee13-aeec-4413-8736-2fee9df2c113"
    }
]
```

You can use it like this for now, but when ready, change to:
```json
"value": "{{datastore.authcode}}"
```

---

## 🧪 Testing Checklist

Before using in production, test with:

**Test Webhook Payload:**
```json
{
  "Item": "61121042",
  "SalesPrice1": 3000.00,
  "CostPrice": 1200.00
}
```

### Expected Flow:
1. ✅ Module 2: Receives webhook
2. ✅ Module 11: Gets AccessToken
3. ✅ Module 6: Gets 250 quotation lines
4. ✅ Module 15: Loops through each line (one at a time)
5. ✅ Module 13 Filter: **ONLY line with Data4="61121042" passes**
6. ✅ Module 13 Update: Updates QuotationLineId=12 (the matching line)

### Verify in webCRM:
- Find QuotationLine 12 (has Data4="61121042")
- Price should be updated to: 3000.00 ✅
- All other lines should BE UNCHANGED ✅

---

## 📋 Summary

Your scenario is **~95% correct**! Just verify:

- [ ] Module 13 has the Filter condition set to: `{{15.QuotationLineData4}} equals {{2.Item}}`
- [ ] Run a test with item "61121042"
- [ ] Confirm only that one line updates (not all 250)
- [ ] Check webCRM to see the new price

If the filter condition isn't showing in Module 13, add it like this:

1. Click on Module 13
2. Look for **Filter** (should be between Module 15 and the URL field)
3. If missing, click "Add filter"
4. Set: `{{15.QuotationLineData4}}` **equals** `{{2.Item}}`
5. Save

---

## 🚀 Next Steps

1. **Verify the filter condition** in Module 13
2. **Test with sample data** 
3. **Check webCRM** to confirm correct line updated
4. **Commit the updated blueprint** to Git
5. **(Optional) Move authCode to datastore** for security

**The hard part is done!** Your scenario structure is correct now. 🎉
