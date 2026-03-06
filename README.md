# Infomail → webCRM Automation

A Make.com automation that processes incoming "Request a Quote" emails and automatically creates or updates company and contact records in webCRM.

---

## Overview

When a quote-request email arrives at the Eilersen inbox, this automation:

1. **Parses** the sender's name, email, phone, company, and country from the email body
2. **Looks up** the email in webCRM to see if the contact already exists
3. **Creates or updates** the company and contact records accordingly
4. Handles the special case of contacts moving out of the generic "Spare parts request" bucket

For a complete walkthrough of every module and decision branch, see [MODULE_NOTES.md](MODULE_NOTES.md).

---

## Project Structure

```
.
├── Infomail - webCRM automation.blueprint.json    # The Make.com scenario (main deliverable)
├── MODULE_NOTES.md                                # Detailed notes on every module + script
├── README.md                                      # This file
├── requirements.txt                               # Python dependencies
├── .env.example                                   # Example environment variables
│
├── docs/                                          # Reference documentation
│   ├── QUICKSTART.md                              #   5-minute setup guide for the API tools
│   ├── CHEATSHEET.md                              #   One-page API command reference
│   ├── Infomail webCRM automation flow.png        #   Visual flow diagram
│   └── From Spare parts requests, new company.png #   "Spare parts" route diagram
│
├── api-tools/                                     # Python scripts for testing the webCRM API
│   ├── README.md                                  #   What each script does
│   ├── test_webcrm.py                             #   Reusable WebCRMClient class (core library)
│   ├── basic_connection_test.py                   #   Quick "can I connect?" check
│   ├── check_email.py                             #   Diagnose which route an email triggers
│   ├── find_email.py                              #   Page-by-page search for an email
│   ├── test_search_methods.py                     #   Compare API search/filter approaches
│   ├── fetch_all_companies.py                     #   Dump all organisations with pagination
│   └── debug/                                     #   Raw API exploration scripts
│       ├── debug_api.py                           #     Field names, response format
│       ├── debug_api2.py                          #     Page counts, search endpoint tests
│       ├── debug_api3.py                          #     All filtering methods tested
│       └── debug_api4.py                          #     Large page-size limits
│
└── .gitignore
```

---

## Getting Started

### 1. Import the Make.com Blueprint

1. In [Make.com](https://www.make.com), create a new scenario
2. Click **⋯ → Import Blueprint**
3. Upload `Infomail - webCRM automation.blueprint.json`
4. Configure the email connection and webCRM API token inside Make.com

### 2. Run the API Tools (optional, for testing/debugging)

```powershell
# Create & activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create your .env from the example
copy .env.example .env
# Then edit .env and add your real WEBCRM_TOKEN

# Quick connection test
cd api-tools
python basic_connection_test.py

# Check what the automation would do for a specific email
python check_email.py
```

See [api-tools/README.md](api-tools/README.md) for details on every script.

---

## How the Automation Works

```
Email arrives
  └─ Parse: Name, Email, Phone, Company, Country
       └─ Valid lead? (has company + email contains @)
            └─ Authenticate with webCRM API
                 └─ Does this email exist in webCRM?
                      │
                      ├─ NO → Does the company exist?
                      │         ├─ NO  → Create Company + Create Contact
                      │         └─ YES → Create Contact under existing company
                      │
                      └─ YES → Same company as in email?
                               ├─ YES → STOP (already correct, no duplicates)
                               ├─ NO, real company → Create Contact under new company
                               └─ "Spare parts request" → Mark old Resigned,
                                    Create Company (if new) + Create Contact
```

Full details with every module ID: [MODULE_NOTES.md](MODULE_NOTES.md)

---

## Key Concepts

| Term | Meaning |
|------|---------|
| **Organisation** | A company record in webCRM |
| **Person** | A contact record, linked to an Organisation |
| **"Spare parts request"** | A catch-all company for unassigned contacts — the automation moves people out of it |
| **Auth Code** | Your API token (in `.env`), exchanged for a temporary Access Token |
| **`/Queries` endpoint** | webCRM's SQL-like search — the reliable way to look up by exact field value |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `401 Unauthorized` | Regenerate token in webCRM Settings → API |
| Email not being processed | Check subject is exactly `"a quote request"` or `"request from website"` |
| Contact created under wrong company | Verify company name spelling matches between email and webCRM |
| `.env` not loading | Ensure it's in the project root, named exactly `.env` (not `.env.txt`) |

---

## Safety & Anti-Spam

- **Email validation:** Emails without `@` in the address are rejected before any API calls.
- **Duplicate contacts:** If a person emails again from the same company, the automation stops — no duplicate contact created.
- **Existing data is never overwritten:** The automation only *creates* new records. It never updates names, phones, or other fields on existing contacts (protects against spam polluting real data).
- **"Resigned" only on fake bucket:** Only contacts under "Spare parts request" are marked Resigned. Real-company contacts are never modified.
- **Company matching is case-insensitive:** "tekniko", "TEKNIKO", and "Tekniko" all resolve to the same company — no accidental duplicates.
- **SQL injection safe:** All user-provided values (email, company name) are escaped before being used in SQL queries.

---

## Resources

- [WebCRM API Documentation](https://api.webcrm.com/docs)
- [Make.com Documentation](https://www.make.com/en/help)
- [docs/QUICKSTART.md](docs/QUICKSTART.md) — Setup guide for the Python API tools
- [docs/CHEATSHEET.md](docs/CHEATSHEET.md) — Quick API command reference

