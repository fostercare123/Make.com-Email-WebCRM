# Changelog — Internship Daily Log

> **Project:** Make.com Email → webCRM Automation  
> **Intern:** IT Intern  
> **Period:** 2026-02-23 → 2026-03-09  

---

## 2026-02-23 (Sunday) — Project Kickoff

### What I Did
- Created the Git repository and initial project structure.
- Wrote the first Python script (`test_webcrm.py`) to connect to the webCRM REST API.
- Tested basic authentication and data retrieval from the API.

### Files Created
- `.gitignore` — Git ignore rules
- `test_webcrm.py` — First webCRM API test script (authentication + basic calls)
- `webCRM OpportunityID 168180.txt` — Sample API response for reference

### What I Learned
- How the webCRM REST API authentication works (POST to `/Auth/ApiLogin` → returns Bearer token).
- How to read API responses and understand the data structure.

---

## 2026-02-24 (Monday) — Building the API Client

### What I Did
- Expanded the API test script significantly (~293 lines) — turned it into a "Postman in Python" tool that can test multiple API endpoints interactively.
- Created a proper `README.md` (+227 lines) documenting the project purpose, setup, and usage.
- Added `requirements.txt` with Python dependencies (`requests`, `python-dotenv`).
- Created a separate `test_auth.py` script to isolate authentication testing.
- Improved `.gitignore` to properly exclude `.env` files with API keys.

### Files Changed
- `test_webcrm.py` — Major expansion: 100 → 293+ lines, multiple API endpoints
- `README.md` — Created: +227 lines of project documentation
- `requirements.txt` — Created: Python dependencies
- `test_auth.py` — Created: Dedicated auth test script
- `.gitignore` — Updated for better security

### What I Learned
- How to structure a Python project with environment variables (`.env` files) for secrets.
- How to use `requests` library for REST API calls with Bearer token auth.
- Importance of keeping API keys out of version control.

---

## 2026-02-25 (Tuesday) — API Exploration & Documentation

### What I Did
- **Deleted** the sample opportunity file (no longer needed).
- **Updated** `requirements.txt` with correct dependency versions.
- **Created extensive documentation:**
  - `CHEATSHEET.md` (+133 lines) — Quick reference for webCRM API calls.
  - `QUICKSTART.md` (+101 lines) — Getting started guide for new developers.
  - Expanded `README.md` significantly (+177 lines).
- **Wrote 12 new test scripts** to explore different webCRM API endpoints:
  - `test_products.py` — Product data retrieval
  - `check_opp_structure.py` — Opportunity structure analysis
  - `discover_endpoints.py` — API endpoint discovery
  - `explore_opportunities.py` — Opportunity data exploration
  - `test_quotation_lines.py` — Quotation line querying
  - `test_quotation_lines_structure.py` — Quotation line field mapping
  - `test_quotations.py` — Quotation data retrieval
  - `min_test.py`, `quick_test.py`, `test_endpoints.py`, `test_opp_lines.py`, `test_products_fields.py`
- **Created Make.com analysis documents:**
  - `MAKE_COM_SOLUTION.md` (+267 lines) — Documenting the Make.com scenario design.
  - `analyze_swagger.py` (+145 lines) — Script to parse the webCRM Swagger/OpenAPI spec.
  - `complete_implementation.py` (+265 lines) — Reference implementation in Python.

### Files Created/Changed
- 12 new test scripts (~691 lines total)
- 3 new analysis files (~677 lines total)
- 3 documentation files updated (~580 lines added)

### What I Learned
- The webCRM API has endpoints for Persons, Organisations, Opportunities, Quotations, QuotationLines, and Products.
- How to use the SQL-like query endpoint (`/Queries`) to search for records.
- How QuotationLines link to Quotations and how item numbers map between systems.
- Started understanding the Make.com scenario structure that would automate the workflow.

---

## 2026-02-26 (Wednesday) — Major Cleanup & Make.com Scenario Fix

### What I Did

**Morning — Project Cleanup:**
- Removed 16 obsolete test scripts that were only needed during exploration (-950 lines).
- Kept only `test_webcrm.py` (the main comprehensive tester) and `basic_connection_test.py` (quick health check).
- Updated `CHEATSHEET.md` and `README.md` with cleaner documentation.

**Afternoon — Make.com Scenario Analysis:**
- Wrote `MAKE_COM_ANALYSIS.md` (+421 lines) — a full review of the existing Make.com automation scenario.
- **Found a critical bug:** The QuotationLine filtering module was matching ALL quotation lines instead of just the one with the correct item number. This meant the automation was updating wrong data.
- Documented security issue: API key was hardcoded in the scenario instead of stored securely.

**Afternoon — Rebuild Guide & Fix:**
- Wrote `MAKE_COM_REBUILD_GUIDE.md` (+302 lines) — step-by-step instructions to fix the scenario:
  - Add an Iterator module to loop through quotation lines one by one.
  - Add a Filter module to match `QuotationLineData4` to the item number.
  - Update Module 13 to work with a single line instead of an array.
- Updated the analysis to reference the Data Store approach for secure key storage.
- Created `BLUEPRINT_VERIFICATION.md` (+125 lines) — checklist to verify the fix works correctly.
- **Tested the scenario — working correctly** with Iterator + Filter approach.

**End of day — Updated `.gitignore`.**

### Files Created
- `MAKE_COM_ANALYSIS.md` — Comprehensive scenario analysis (+421 lines)
- `MAKE_COM_REBUILD_GUIDE.md` — Step-by-step fix guide (+302 lines)
- `BLUEPRINT_VERIFICATION.md` — Test/verification checklist (+125 lines)
- `basic_connection_test.py` — Quick API health check (+14 lines)

### Files Removed
- 16 exploratory test scripts that served their purpose (-950 lines)

### What I Learned
- How Make.com scenarios work: modules, routes, filters, iterators, data stores.
- The importance of filtering in loops — without a filter, an iterator processes ALL items.
- How to securely store API keys in Make.com Data Stores instead of hardcoding.
- How to debug a Make.com scenario by tracing data flow module by module.

---

## 2026-03-06 (Thursday) — Project Restructure & New Tools

### What I Did

**Major project reorganization:**
- Removed old analysis documents that were superseded by the working solution:
  - `MAKE_COM_ANALYSIS.md`, `MAKE_COM_REBUILD_GUIDE.md`, `MAKE_COM_SOLUTION.md`, `BLUEPRINT_VERIFICATION.md`, `complete_implementation.py`
- Created proper folder structure:
  - `api-tools/` — All Python API scripts
  - `api-tools/debug/` — Debug/troubleshooting scripts
  - `docs/` — Documentation and diagrams
- Moved existing files into the new structure.

**New documentation:**
- Created `MODULE_NOTES.md` (+225 lines, later expanded +90 lines) — comprehensive notes on every module in the Make.com automation, including the decision tree (Router branches A, B, B1, B2).
- Created `api-tools/README.md` (+48 lines) — guide for using the API tools.
- Updated and simplified the main `README.md`.
- Added flow diagrams to `docs/` folder (PNG images showing the automation flow).

**New API tools:**
- `api-tools/check_email.py` (+102 lines) — Check if an email exists in webCRM.
- `api-tools/find_email.py` (+65 lines) — Search for a person by email address.
- `api-tools/test_search_methods.py` (+64 lines) — Compare different search approaches.
- `api-tools/fetch_all_companies.py` (+263 lines) — Download all companies from webCRM.
- `api-tools/debug/debug_api.py` through `debug_api4.py` — Progressive debugging scripts for API issues.

**Expanded MODULE_NOTES.md** with additional detail on routes and module behavior.

### Files Created
- `MODULE_NOTES.md` — Full module-by-module documentation (+315 lines total)
- `api-tools/README.md` — API tools guide (+48 lines)
- `api-tools/check_email.py`, `find_email.py`, `test_search_methods.py`, `fetch_all_companies.py`
- `api-tools/debug/debug_api.py` through `debug_api4.py`
- `docs/` — Flow diagram images
- Updated `docs/QUICKSTART.md` (+24 lines)

### Files Removed
- 5 old analysis/guide documents (replaced by MODULE_NOTES.md)

### What I Learned
- How to organize a growing project into a clear folder structure.
- The complete decision tree of the Make.com automation: how it routes new vs. existing contacts, and new vs. existing companies.
- How to write debug scripts that progressively isolate API issues.

---

## 2026-03-09 (Sunday) — Fix Email Parsing for HTML Emails & Encoding

### Problem
The Make.com automation stopped silently at Module 2 (Text Parser). Module 2 showed green but produced 0 output bundles, so the rest of the flow never ran. This is the "Infomail – webCRM automation" scenario that creates contacts in webCRM from quote-request emails sent by the TYPO3 website (eilersen.com).

### Root Causes Found & Fixed

**1. Regex couldn't handle email links on separate lines**
- The original `(\S+@\S+).*\n+\s*Phone` used `.*` which can't cross newlines.
- When the email link `[testhejsa@eilersen.com]` appeared on its own line (as links do in this email format), the regex failed to reach "Phone".
- **Fix:** Changed to `(\S+@\S+)[\s\S]*?\n[ \t]*Phone` — allows matching across multiple lines lazily.

**2. `\s*` and `\n+` competing for newline characters**
- Throughout the regex, `\s*` was placed next to `\n+`. Since `\s` matches `\n`, both patterns competed for the same characters. Python resolved this via backtracking, but Make.com's JS/V8 engine didn't.
- **Fix:** Replaced all `\s*` with `[ \t]*` (horizontal whitespace only). Now only `\n+` consumes newlines — zero ambiguity.

**3. HTML-only emails produced empty input**
- The mapper used `1.text` (plain text MIME part). The website emails are HTML-only, so `1.text` was null/empty. The regex saw an empty string and matched nothing.
- **Fix:** Changed mapper to `if(length(1.text) > 0; toString(1.text); toString(stripHtml(1.html)))` — falls back to stripping HTML tags from `1.html` when no plain text exists.

**4. UTF-8 double-encoding (mojibake) garbled company/person names**
- The TYPO3 website sends UTF-8 text, but by the time Make.com reads the email, bytes are misinterpreted as Latin-1. This turns `ø` → `Ã¸`, `å` → `Ã¥`, etc.
- Make.com's `toBinary()`/`toString()` doesn't support `ISO-8859-1` encoding, so a programmatic re-encode wasn't possible.
- **Fix:** Added a chain of 31 `replace()` calls in the mapper that fix the most common mojibake patterns before the regex runs:
  - 21 lowercase: ø, å, æ, é, ü, ö, ä, ñ, ç, â, ë, ï, ì, ó, ò, ù, ý, á, í, ð, ú
  - 10 uppercase: Å, Æ, Ø, É, Ö, Ü, Ä, Ñ, À, Ç

### Final Module 2 Regex
```
Full[ \t]*Name[ \t]*\n+[ \t]*(\S+)[ \t]*(.*?)[ \t]*\n+[ \t]*Email[ \t]*Address[ \t]*\n+[ \t]*(\S+@\S+)[\s\S]*?\n[ \t]*Phone[ \t]*\n+[ \t]*(.*?)[ \t]*\n+[ \t]*Compan[ \t]*y[ \t]*Name[ \t]*\n+[ \t]*(.*?)[ \t]*\n+[ \t]*Country[ \t]*\n+[ \t]*(.*?)[ \t]*\n
```

**5. Duplicate contact creation — wrong module reference in filter**
- When a person already existed in webCRM (Route B "Email Found"), the scenario still created a duplicate contact every time.
- **Root cause:** Module 14's filter "NOT Spare Parts AND Different Company" compared `{{11.data.OrganisationName}}` to the email's company name — but Module 11 is in the "Email Not Found" branch (Route A) and never runs in Route B. Its value was always empty/null, so the "different company" check was always true.
- **Fix:** Changed `11.data.OrganisationName` → `12.data.OrganisationName` (Module 12 = "Get Person's Organisation", which actually runs in Route B and returns the person's current company).
- Now: same person + same company → filter blocks → no duplicate. Only proceeds when the person has genuinely moved to a different company.

### Full blueprint audit
After the Module 14 fix, audited all 26 module data references (`{{N.data...}}`) across the entire blueprint. All other references are correct — each module only references modules that run upstream in the same branch.

**Three edge cases noted (not bugs, design choices):**
1. If a person exists with `OrganisationId = 0` (no company), Module 12 calls `/Organisations/0` which would error. Unlikely since Module 3 already filters out empty companies.
2. Multiple people with the same email: only the first match (`data[1]`) is used.
3. No update path for existing contacts at the same company — phone/name changes are silently ignored.

### Files Changed
- `Infomail - webCRM automation.blueprint.json` — Module 2 regex pattern + mapper expression, Module 14 filter fix
- `CHANGELOG.md` — Created (this file)

### What I Learned
- Make.com uses a JavaScript/V8 regex engine, which handles backtracking differently than Python's.
- `\s*` matches newlines — when placed next to `\n+`, they compete. Always use `[ \t]*` for horizontal-only whitespace.
- HTML-only emails have no `text` MIME part — must fall back to `stripHtml(html)`.
- Mojibake happens when UTF-8 bytes are read as Latin-1. When you can't re-encode programmatically, a chain of `replace()` calls is a valid workaround.
- How to debug Make.com modules: green doesn't mean "it worked" — it means "no error". Zero output bundles means the match/filter silently rejected the input.
- Cross-branch module references are a silent killer — a filter referencing a module from a different route gets null data, making the condition always pass (or always fail). Always verify that `{{N.data}}` points to a module in the **same execution path**.

### Known Limitation
Uppercase letters whose UTF-8 second byte is a C1 control character (0x80–0x9F) may have that byte stripped by the email pipeline. If an uppercase Å, Æ, or Ø appears as a lone `Ã` at the end of a field, it means the second byte was lost upstream. The permanent fix for this would be correcting the `Content-Type` charset header on the TYPO3 website's outgoing emails.
