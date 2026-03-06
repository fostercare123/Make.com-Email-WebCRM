# Module Notes — Infomail → webCRM Automation

> **Audience:** Anyone new to this project.  
> **What this project does:** When a "Request a Quote" email arrives in the Eilersen inbox, this automation parses the email, looks up the sender in webCRM, and creates/updates the company and contact records automatically.

---

## How the System Works (Big Picture)

```
Incoming email  →  Parse contact details  →  Look up in webCRM  →  Create/update records
```

There are two main parts:

1. **The Make.com Blueprint** (`Infomail - webCRM automation.blueprint.json`) — The live automation that runs in the cloud.
2. **Python Scripts** — Helper scripts used for testing, debugging, and validating the webCRM API during development.

---

## Part 1: The Make.com Automation (Blueprint)

The file `Infomail - webCRM automation.blueprint.json` is a Make.com scenario. You import it into [Make.com](https://www.make.com) to run the automation. Here is what each module does, step by step:

### Step 1 — Trigger: Watch for New Emails (Module 1)

- **What:** Monitors the `info (vnn@eilersen.com)` inbox for unread emails.
- **Runs:** Every time a new unread email arrives.

### Step 2 — Parse the Email (Module 2: Text Parser)

- **What:** Uses a regex pattern to extract these fields from the email body:
  - `$1` = First Name
  - `$2` = Last Name
  - `$3` = Email Address
  - `$4` = Phone
  - `$5` = Company Name
  - `$6` = Country
- **Filter:** Only processes emails where the subject is `"a quote request"` or `"request from website"`. All other emails are ignored.

### Step 3 — Authenticate with webCRM (Module 3: HTTP - ApiLogin)

- **What:** Exchanges the API auth code for a temporary Access Token (valid 1 hour).
- **Filter ("Valid Lead"):** Only runs if **both** conditions are met:
  1. Company Name is not empty.
  2. Email Address contains `@` (basic spam/garbage filter).
- **Result:** All following modules use this Access Token for API calls.

### Step 4 — Look Up Person by Email (Module 4: HTTP - Query Person by Email)

- **What:** Runs a SQL query against the webCRM `/Queries` endpoint:
  ```sql
  SELECT PersonId, PersonEmail, PersonOrganisationId
  FROM Person
  WHERE PersonEmail = '<parsed email>'
  ```
- **Note:** The email value is SQL-escaped (single quotes replaced with `''`) to prevent query breakage.
- **Result:** Returns matching person(s), or an empty array if the email is new.

### Step 5 — Router (Module 5)

This is the main decision point. It branches into **two routes** based on whether the email was found:

---

### ROUTE A — Email NOT Found (New Lead)

> *"We've never seen this email before — create everything fresh."*

#### Module 6: Query Org by Name
- **Filter:** `length(Module 4 results) == 0` (email was NOT found)
- **What:** Checks if the company name from the email already exists in webCRM.

#### Module 7: Router — Does the company exist?

**Route A1 — Company NOT found (create both):**
- **Module 8: Create Company** — Creates a new Organisation with the parsed company name, country, currency = EUR, and tags it with `"Inbox Automation"`.
- **Module 9: Create Contact** — Creates a new Person linked to the company just created in Module 8.

**Route A2 — Company found (create contact only):**
- **Module 10: Create Contact** — Creates a new Person linked to the existing company found in Module 6.

---

### ROUTE B — Email Found (Returning Contact)

> *"This person already exists in webCRM — but are they in the 'Spare parts request' bucket?"*

#### Module 11: Get Person's Organisation
- **Filter:** `length(Module 4 results) > 0` (email WAS found)
- **What:** Fetches the Organisation that this person currently belongs to.

#### Module 12: Router — Is it a "Spare parts request" organisation?

**Route B1 — NOT "Spare parts request" AND different company (contact changing companies):**

> *"Person exists at a real company, but the email's company name is different — they may have moved. Create a new contact under the new company."*

- **Module 18: Query Org by Name** — Looks up the company name from the email.
  - **Filter ("NOT Spare Parts AND Different Company"):** Only proceeds if **both**:
    1. Current org ≠ "Spare parts request"
    2. Current org ≠ email's company name (case-insensitive comparison)
  - **If the person is already at the same company as in the email, this route is blocked → no duplicate contact created.**
- **Module 21: Router:**
  - **Module 22 + 23:** Company not found → Create new company + contact.
  - **Module 19:** Company found → Create contact under existing company.

**Route B2 — IS "Spare parts request" (needs reorganization):**

> *"Person was previously filed under the generic 'Spare parts request' company. Now they've submitted a real quote request, so we reorganize them."*

- **Module 13: Mark Old Contact as Resigned** — Sets `PersonStatus = "Resigned"` on the old contact record.
- **Module 14: Query Org by Name** — Looks up the real company name from the email.
- **Module 16: Router:**
  - **Module 17 + 20:** Company not found → Create new company + new contact.
  - **Module 15:** Company found → Create new contact under existing company.

---

### Flow Summary (Decision Tree)

```
Email arrives
  └─ Parse: Name, Email, Phone, Company, Country
       └─ Valid lead? (has company + email contains @)
            └─ Authenticate with webCRM API
                 └─ Query: Does this email already exist in webCRM?
                      │
                      ├─ NO (Route A) ──── Query: Does the company exist?
                      │                       ├─ NO  → Create Company + Create Contact
                      │                       └─ YES → Create Contact under existing company
                      │
                      └─ YES (Route B) ── Get person's current organisation
                                             │
                                             ├─ Same company as email? → STOP (no action, no duplicates)
                                             │
                                             ├─ Different real company (Route B1)
                                             │     └─ Query: Does the (new) company exist?
                                             │          ├─ NO  → Create Company + Create Contact
                                             │          └─ YES → Create Contact under existing company
                                             │
                                             └─ IS "Spare parts request" (Route B2)
                                                   └─ Mark old contact as Resigned
                                                        └─ Query: Does the (new) company exist?
                                                             ├─ NO  → Create Company + Create Contact
                                                             └─ YES → Create Contact under existing company
```

---

## Part 2: Python Scripts (in `api-tools/`)

These scripts are **not** part of the live automation. They are developer tools for testing and debugging the webCRM API. All located in the `api-tools/` folder.

### Core Library

| File | What It Does |
|------|-------------|
| **api-tools/test_webcrm.py** | The main reusable API client. Contains the `WebCRMClient` class which handles authentication automatically. All other scripts import from here. Run it directly (`python test_webcrm.py`) to execute a suite of connection and data-fetch tests. |

### Testing Scripts

| File | What It Does |
|------|-------------|
| **api-tools/basic_connection_test.py** | Simplest possible test — just checks "can I connect to webCRM?" If it prints `✅ Connected`, your `.env` credentials work. |
| **api-tools/check_email.py** | Checks if a specific email (e.g. `buy@ayuguoky.com`) exists in webCRM and whether they belong to the "Spare parts request" company. Prints a **diagnosis** of which route the Make.com automation would take for that email. Great for verifying expected behavior before/after a test run. |
| **api-tools/find_email.py** | Searches through all persons page-by-page (up to 500) to find a specific email. Useful when the API search endpoint doesn't return expected results. |
| **api-tools/test_search_methods.py** | Compares different ways to search for a person by email (`/Persons?PersonEmail=`, `/Persons/Search?term=`, `/Persons` unfiltered). Helped discover that the `PersonEmail` query param does NOT actually filter — only `/Persons/Search` works. |

### Debug Scripts (in `api-tools/debug/`)

| File | What It Does |
|------|-------------|
| **debug/debug_api.py** | Lists every field name in the Organisation response. Searches for specific companies (TEKNIKO, "Spare parts request"). Shows whether the API returns a plain array or wrapped object. |
| **debug/debug_api2.py** | Counts how many pages of Organisations and Persons exist. Tests the `/Search` endpoint for both. |
| **debug/debug_api3.py** | Comprehensive test of every filtering/search approach the API supports: query params, GET search, POST search, field filters. Determines which actually work. |
| **debug/debug_api4.py** | Tests whether the API allows large page sizes (2000, 5000, 10000). Found the practical limits for bulk fetching. |

### Utility Scripts

| File | What It Does |
|------|-------------|
| **api-tools/fetch_all_companies.py** | Fetches **every** company from webCRM with automatic pagination (250 per page), retry logic for failures, and token caching. Run it to get a full dump of all organisations. |

---

## Part 3: Documentation & Config

| File | What It Does |
|------|-------------|
| **README.md** | Project overview, getting started, how the automation works. |
| **docs/QUICKSTART.md** | 5-minute getting-started guide for the Python API tools. |
| **docs/CHEATSHEET.md** | One-page reference of common API operations (copy-paste code snippets). |
| **requirements.txt** | Python dependencies: `requests` and `python-dotenv`. Install with `pip install -r requirements.txt`. |
| **.env** *(not in repo)* | Your secrets: `WEBCRM_BASE_URL` and `WEBCRM_TOKEN`. Never commit this file. |

---

## Key Concepts for Newcomers

### webCRM Authentication (2-step)
1. You have an **Auth Code** (API token stored in `.env`).
2. You POST it to `/Auth/ApiLogin` to get a temporary **Access Token** (valid 1 hour).
3. All API calls use the Access Token as a `Bearer` token.

### webCRM Data Model
- **Organisation** = Company (has an `OrganisationId` and `OrganisationName`)
- **Person** = Contact (has a `PersonId`, `PersonEmail`, linked to an Organisation via `PersonOrganisationId`)
- **"Spare parts request"** = A special catch-all company for unassigned contacts. The automation moves people out of it when they submit a real quote.

---

## API Findings

These were discovered during development and are worth knowing:

- **Company name matching is case-insensitive.** webCRM's `=` operator in `/Queries` treats `'tekniko'`, `'Tekniko'`, and `'TEKNIKO'` identically. No `LOWER()`/`UPPER()` wrapper needed.
- **`/Persons?PersonEmail=` does NOT filter.** Only `/Persons/Search?term=` and `/Queries` with a SQL `WHERE` clause actually work for email lookups.
- **"Resigned" is only set on "Spare parts request" contacts.** Contacts at real companies are never modified — only new contacts are created alongside them.

---

## Changelog

### 2026-03-06 — Dedup & safety hardening

**Problem:** Sending two identical emails created duplicate contacts under the same company.

**Changes made to the blueprint:**

1. **Module 3 filter — added email validation.**
   - Old: only checked company name ≠ empty.
   - New: also requires email contains `@`. Blocks spam/garbage before any API calls.

2. **Module 4 — SQL-escaped email value.**
   - The person-lookup query now escapes single quotes in the email (`'` → `''`), matching how company-name queries were already handled.

3. **Module 18 filter — added same-company dedup guard (Route B1).**
   - Old: only checked org ≠ "Spare parts request".
   - New: also checks org ≠ email's company name (case-insensitive). If the person is already at the correct company, the route is blocked → no duplicate contact.

**Not changed (by design):**

- **No auto-update of existing contacts.** When a known person re-submits from the same company, the automation does nothing. This is intentional — updating fields (phone, name) from inbound email could overwrite good data with spam data.
- **No "Resigned" on real-company contacts.** Only contacts under the fake "Spare parts request" company get marked Resigned when reorganized. Contacts at real companies are left untouched.

### The `/Queries` Endpoint
The Make.com automation uses webCRM's `/Queries` endpoint which accepts SQL-like queries:
```
/Queries?script=SELECT ... FROM Person WHERE PersonEmail = 'someone@example.com'
```
This is the reliable way to search by exact field values (plain REST filters don't always work — see `api-tools/test_search_methods.py`).

---

## Running a Test Today

1. **Verify API connectivity:**
   ```powershell
   cd api-tools
   python basic_connection_test.py
   ```

2. **Check what the automation will do for a given email:**
   Edit the `email` variable in `api-tools/check_email.py`, then:
   ```powershell
   python check_email.py
   ```

3. **After the automation runs, verify the result:**  
   Use `check_email.py` again to confirm the contact/company was created correctly.
