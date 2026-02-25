# 📋 WebCRM API Cheat Sheet

Quick reference for common WebCRM API operations.

## Setup (One-Time)

```python
from test_webcrm import WebCRMClient
import os
from dotenv import load_dotenv

load_dotenv()
client = WebCRMClient(os.getenv("WEBCRM_BASE_URL"), os.getenv("WEBCRM_TOKEN"))
```

---

## 🏢 Companies (Organisations)

```python
# List all companies
companies = client.get_organisations(page=1, size=20)

# Get a specific company
company = client.get_organisation_by_id("2")

# Print company names
for c in companies:
    print(f"{c['OrganisationId']}: {c['OrganisationName']}")
```

---

## 💼 Deals (Opportunities)

```python
# List all deals
deals = client.get_opportunities(page=1, size=20)

# Get a specific deal
deal = client.get_opportunity_by_id("168180")

# Print deal info
for d in deals:
    print(f"{d['Name']} - Value: {d.get('Value', 0)}")
```

---

## 👤 Contacts (Persons)

```python
# List all contacts
contacts = client.get_persons(page=1, size=20)

# Get contacts for a specific company
company_contacts = client.get_persons(org_id="2", page=1, size=20)

# Create a new contact
new_contact = client.create_person({
    "FirstName": "John",
    "LastName": "Doe",
    "Email": "john@example.com",
    "OrganisationId": "2"
})

# Print contact names
for p in contacts:
    print(f"{p['PersonFirstName']} {p['PersonLastName']}")
```

---

## 🔧 Common Patterns

### Pagination (Get All Results)

```python
all_companies = []
page = 1
while True:
    result = client.get_organisations(page=page, size=100)
    if not result:
        break
    all_companies.extend(result)
    page += 1
```

### Find by Name

```python
companies = client.get_organisations(page=1, size=250)
eilersen = [c for c in companies if "Eilersen" in c['OrganisationName']]
```

### Debug Mode

```python
# Turn on detailed logging
client = WebCRMClient(BASE_URL, TOKEN, debug=True)

# Turn off for production
client = WebCRMClient(BASE_URL, TOKEN, debug=False)
```

---

## ⚡ Quick Commands

| What You Want | Code |
|---------------|------|
| List companies | `client.get_organisations(page=1, size=20)` |
| Get company #2 | `client.get_organisation_by_id("2")` |
| List deals | `client.get_opportunities(page=1, size=20)` |
| Get deal #168180 | `client.get_opportunity_by_id("168180")` |
| List all contacts | `client.get_persons(page=1, size=20)` |
| Company contacts | `client.get_persons(org_id="2")` |
| Test connection | `client.test_connection()` |

---

## 🆘 Troubleshooting

| Error | Solution |
|-------|----------|
| `Missing WEBCRM_BASE_URL` | Create `.env` file with credentials |
| `401 Unauthorized` | Regenerate token in WebCRM Settings → API |
| `404 Not Found` | Check that resource ID exists |
| Old data showing | Restart Python terminal |

---

**For more details, see:** [README.md](README.md) | [QUICKSTART.md](QUICKSTART.md)
