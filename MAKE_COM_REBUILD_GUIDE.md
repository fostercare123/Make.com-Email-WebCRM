# Make.com Scenario Rebuild Guide: Fix the Critical Bug

## 🎯 What We're Fixing

Your current scenario tries to update **ALL 250 quotation lines** instead of just the matching one.

**Before (❌ Broken):**
```
Webhook → Get Token → Get ALL Lines → Update ALL 250 Lines
```

**After (✅ Fixed):**
```
Webhook → Get Token → Get ALL Lines → Iterator → Filter → Update ONLY Matching Line
```

---

## 📋 Your Current Modules (Keep These)

- **Module 2:** Webhook Trigger ✓
- **Module 11:** Get Access Token ✓ (updated to use Data Store)
- **Module 6:** Search Items (Get QuotationLines) ✓

## ➕ New Modules to Add

- **Module X:** Iterator (loops through lines one at a time)
- **Module Y:** Filter (checks if line matches)
- **Module 13:** Update Price (modify the changed module reference)

---

## 🔧 Step 1: Add Iterator Module

The Iterator will take the array of 250 lines and process them **one at a time**.

### In Make.com:

1. **Click on Module 6** (Search Items)
2. Click the **circle/dot icon to the right** to add a new module after it
3. Search for: `Array Iterator`
4. Select **`Flow control → Array Iterator`**

### Configure Iterator:

```
Array: {{6.data}}
```

That's it! This takes your array of lines and repeats the following modules for each line.

**What it does:**
- Takes: Array of 250 quotation lines
- Outputs: One line at a time as `{{item}}`

---

## 🚪 Step 2: Add Filter Module

The Filter will only continue if the line's item number matches.

### In Make.com:

1. Click the **circle/dot icon** on the right side of the Iterator module
2. Search for: `Filter`
3. Select **`Flow control → Filter`**

### Configure Filter:

The Filter needs **one condition** to pass:

```
If: {{item.QuotationLineData4}}
    Equals
    {{2.Item}}
```

**Breaking it down:**
- `{{item.QuotationLineData4}}` = The item number stored in webCRM
- `{{2.Item}}` = The item number from the Uniconta webhook
- If they match → Continue to Module 13
- If they don't match → Skip Module 13 for this line

---

## 🔄 Step 3: Update Module 13 (Update Price)

Now that we have only ONE matching line (from the Filter), change the URL and body.

### In Module 13, Change These:

**Current URL:**
```
PUT https://api.webcrm.com/QuotationLines/{{6.data[].QuotationLineId}}
```

**New URL:**
```
PUT https://api.webcrm.com/QuotationLines/{{item.QuotationLineId}}
```

**Current Body:**
```json
{
  "QuotationLineId": {{6.data[].QuotationLineId}},
  "QuotationLinePrice": {{2.SalesPrice1}},
  "QuotationLineCostPrice": {{2.CostPrice}}
}
```

**New Body:**
```json
{
  "QuotationLineId": {{item.QuotationLineId}},
  "QuotationLinePrice": {{2.SalesPrice1}},
  "QuotationLineCostPrice": {{2.CostPrice}}
}
```

**Changes:**
- Remove `[].` from URLs and references
- Use `{{item.fieldname}}` instead of `{{6.data[].fieldname}}`

---

## 📊 Module Flow After Fix

```
Module 2 (Webhook)
    ↓
Module 11 (Get Token)
    ↓
Module 6 (Get ALL Lines)
    ↓
Module X (Iterator) ← NEW: Loop through each line
    ↓
Module Y (Filter) ← NEW: Check if line matches
    ↓
Module 13 (Update Price) ← UPDATED: Use {{item}} instead of {{6.data[]}}
```

---

## 🧪 Testing the Fix

### Test Data
Use this Uniconta webhook payload:
```json
{
  "Item": "61121042",
  "SalesPrice1": 3000.00,
  "CostPrice": 1200.00
}
```

### Expected Flow

1. **Module 2:** Receives webhook with Item = "61121042"
2. **Module 11:** Gets AccessToken ✅
3. **Module 6:** Gets 250 quotation lines ✅
4. **Module X (Iterator):** Loops through each line
   - Iteration 1: Line with Data4 = "69210001" → Goes to Filter
   - Iteration 2: Line with Data4 = "61121042" → Goes to Filter ← **MATCH!**
   - Iteration 3: Line with Data4 = "66911003" → Goes to Filter
   - ... (249 more iterations)
5. **Module Y (Filter):** Only line with Data4 = "61121042" passes ✅
6. **Module 13:** Updates ONLY QuotationLine 12 ✅

### Verify in webCRM
- Open QuotationLine 12 (item 61121042)
- Price should be: 3000.00 ✅
- Other lines should be unchanged ✅

---

## 🎨 Visual Guide: What to Look For

### Iterator Module (Array Iterator)
```
┌─────────────────────────┐
│  Array Iterator         │
│ ─────────────────────── │
│ Array: {{6.data}}       │
│                         │
│ Outputs:                │
│ - item (single line)    │
│ - item.QuotationLineId  │
│ - item.QuotationLineData4
│                         │
└─────────────────────────┘
```

### Filter Module
```
┌─────────────────────────────────┐
│  Filter                         │
│ ───────────────────────────── │
│ Condition:                      │
│                                 │
│ {{item.QuotationLineData4}}     │
│    [equals dropdown]            │
│ {{2.Item}}                      │
│                                 │
│ ✅ If true → continue to next   │
│ ❌ If false → skip to end       │
│                                 │
└─────────────────────────────────┘
```

---

## 📌 Common Mistakes to Avoid

### ❌ Wrong: Keep the old array notation
```
{{6.data[].QuotationLineId}}  ← NO! Updates all 250
```

### ✅ Correct: Use the iterator result
```
{{item.QuotationLineId}}  ← YES! Updates only matched line
```

### ❌ Wrong: Filter condition is backwards
```
{{2.Item}} equals {{item.QuotationLineData4}}  ← Works but confusing
```

### ✅ Correct: webCRM field on left
```
{{item.QuotationLineData4}} equals {{2.Item}}  ← Clear!
```

---

## 🐛 Troubleshooting

### "Iterator not available"
- Make sure you're searching under **Flow control**
- Not under **HTTP** or other category

### "Filter not connecting to Module 13"
- Click the **circle icon** on the right of the Filter module
- It should show the path to Module 13
- If not, add Module 13 after the Filter

### "Module 13 says {{item}} is undefined"
- Make sure Filter is **before** Module 13
- Make sure Iterator is **before** Module 13
- You need both for `{{item}}` to be available

### "All 250 lines still updating"
- Check your Module 13 URL/body
- Make sure you removed the `[]` from the field names
- Make sure you're using `{{item.}}` not `{{6.data[].}}`

---

## 📚 Complete Module Reference

After rebuild, your modules should look like:

| Module | Type | Configuration |
|--------|------|---|
| 2 | Webhook | Listens for Uniconta InvItem updates |
| 11 | HTTP | POST to `/Auth/ApiLogin` with {{datastore.authcode}} |
| 6 | HTTP | GET `/QuotationLines?page=1&size=250` |
| X | Iterator | Array: {{6.data}} |
| Y | Filter | {{item.QuotationLineData4}} equals {{2.Item}} |
| 13 | HTTP | PUT `/QuotationLines/{{item.QuotationLineId}}` |

---

## ✅ Implementation Checklist

- [ ] Add Iterator module after Module 6
  - [ ] Set Array to: `{{6.data}}`
- [ ] Add Filter module after Iterator
  - [ ] Set condition: `{{item.QuotationLineData4}}` equals `{{2.Item}}`
- [ ] Update Module 13 URL
  - [ ] Change to: `https://api.webcrm.com/QuotationLines/{{item.QuotationLineId}}`
- [ ] Update Module 13 Body
  - [ ] Replace `{{6.data[].QuotationLineId}}` with `{{item.QuotationLineId}}`
  - [ ] Keep `{{2.SalesPrice1}}` and `{{2.CostPrice}}` (no changes)
- [ ] Save scenario
- [ ] Test with sample webhook
- [ ] Verify only one line updates
- [ ] Commit changes to Git

---

## 🎉 After Everything Works

Once this is fixed, you can:
1. ✅ Confidently update product prices from Uniconta
2. ✅ Know that only matching items are updated (not all 250!)
3. ✅ Extend the logic to other Uniconta → webCRM syncs
4. ✅ Add error handling and notifications

---

**Questions about any step? Let me know!** 🚀
