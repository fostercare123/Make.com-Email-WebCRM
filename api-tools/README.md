# API Tools

Python scripts for testing and debugging the webCRM API. These are **not** part of the live automation — they're developer tools used during development of the Make.com blueprint.

## Setup

From the project root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # then add your real WEBCRM_TOKEN
```

## Scripts

### Core

| Script | Purpose | Run it when... |
|--------|---------|----------------|
| **test_webcrm.py** | Reusable `WebCRMClient` class. All other scripts import from here. | `python test_webcrm.py` — runs a full connection + data-fetch test suite. |
| **basic_connection_test.py** | Minimal "can I connect?" check. | You just want a quick yes/no on whether `.env` credentials work. |

### Automation Validation

| Script | Purpose | Run it when... |
|--------|---------|----------------|
| **check_email.py** | Looks up a specific email in webCRM and prints which Make.com route would fire (Route A / B1 / B2). | Before or after an automation test run — verifies expected behavior. |
| **find_email.py** | Brute-force page-by-page search for an email across all persons (up to 500). | The search endpoint doesn't return expected results. |
| **test_search_methods.py** | Compares `/Persons?PersonEmail=`, `/Persons/Search?term=`, and unfiltered `/Persons`. | You need to understand which API filter methods actually work. |

### Data Export

| Script | Purpose | Run it when... |
|--------|---------|----------------|
| **fetch_all_companies.py** | Fetches every organisation with auto-pagination (250/page), retry logic, and token caching. | You need a full dump of all companies. |

### debug/ — Raw API Exploration

These were written during initial API investigation. They're kept for reference.

| Script | What it explored |
|--------|-----------------|
| **debug_api.py** | Organisation field names, response format (array vs. object), specific company lookups. |
| **debug_api2.py** | Page counts for Organisations and Persons, `/Search` endpoint behavior. |
| **debug_api3.py** | Every filtering approach: query params, GET search, POST search, field filters. |
| **debug_api4.py** | Maximum page sizes the API allows (2000, 5000, 10000). |
