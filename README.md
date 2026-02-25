# WebCRM API Tester

A lightweight Python utility for testing WebCRM API endpoints directly in code. Think of it as **Postman in Python** — perfect for automating API tests, debugging requests, and validating integrations.

---

## 📚 Documentation

- **🚀 [Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes
- **📋 [Cheat Sheet](CHEATSHEET.md)** - Common commands at a glance
- **📖 Full Documentation** - You're reading it! (below)

---

## Features

✅ Simple API client for testing WebCRM endpoints  
✅ **Automatic authentication** - handles the 2-step token exchange for you  
✅ Built-in debugging output with request/response details  
✅ Support for GET, POST, PUT, DELETE methods  
✅ Clean, organized code with reusable methods  
✅ Error handling and timeout management  
✅ Environment-based configuration (.env)

## Prerequisites

- Python 3.8+
- `requests` library
- `python-dotenv` library
- Valid WebCRM API token (get this from your WebCRM account settings)

## 🔐 How Authentication Works

WebCRM uses a **2-step authentication process**:

1. **Your API Token** (stored in `.env`) is called an "Auth Code"
2. You exchange it for a **temporary Access Token** by calling `/Auth/ApiLogin`
3. The Access Token is used for all subsequent API requests
4. Access tokens expire after 1 hour (3600 seconds)

**Good news:** The `WebCRMClient` class handles this automatically! You just provide your API token once, and it gets fresh access tokens as needed.

## Setup

### 1. Get Your WebCRM API Token

1. Log into your WebCRM account
2. Go to **Settings** → **API** (or **Integrations**)
3. Create a new API token
4. Copy the token (it looks like: `a1b2c3d4-e5f6-7890-abcd-1234567890ef`)
5. Make sure it has **Read/Write** permissions as needed

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate

# Activate it (macOS/Linux)
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests python-dotenv
```

### 4. Create a `.env` File

Create a `.env` file in the project root with your WebCRM credentials:

```bash
# Copy the example file
cp .env.example .env
```

Then edit `.env` and add your real credentials:

```env
WEBCRM_BASE_URL=https://api.webcrm.com
WEBCRM_TOKEN=your-api-token-here
```

Replace `your-api-token-here` with **your actual API token** from step 1.

⚠️ **Never commit the `.env` file to version control!** It's already in `.gitignore`.

### 5. Run Tests

```bash
python test_webcrm.py
```

You should see output like:
```
✅ Connection successful!
✅ Found 5 organisations
✅ Found 5 opportunities
✅ Found 5 persons
```

## Usage Examples

### 🚀 Quick Start - Get Your Companies

The simplest way to get started:

```python
from test_webcrm import WebCRMClient
import os
from dotenv import load_dotenv

# Load your API credentials from .env
load_dotenv()

# Create the client (authentication is automatic!)
client = WebCRMClient(
    os.getenv("WEBCRM_BASE_URL"),
    os.getenv("WEBCRM_TOKEN"),
    debug=False  # Set to True to see detailed output
)

# Get all your companies (called "Organisations" in WebCRM)
companies = client.get_organisations(page=1, size=20)

# Print company names
for company in companies:
    print(f"ID: {company['OrganisationId']}, Name: {company['OrganisationName']}")
```

**Output:**
```
ID: 1, Name: Webcrm A/S
ID: 2, Name: Eilersen Electric Digital Systems A/S
ID: 5, Name: Ek El-Service/Erik Kragh
```

### Basic Connection Test

```python
from test_webcrm import WebCRMClient
import os
from dotenv import load_dotenv

load_dotenv()

client = WebCRMClient(
    os.getenv("WEBCRM_BASE_URL"),
    os.getenv("WEBCRM_TOKEN")
)

# Test connection
if client.test_connection():
    print("✅ Connected to WebCRM successfully!")
```

### Fetch Organisations (Companies)

```python
# Get first 20 organisations
organisations = client.get_organisations(page=1, size=20)

# Get next page
organisations_page2 = client.get_organisations(page=2, size=20)

# Get a specific organisation by ID
org = client.get_organisation_by_id("2")  # Eilersen Electric
print(f"Company: {org['OrganisationName']}")
print(f"Address: {org.get('OrganisationAddress', 'N/A')}")
```

### Fetch Opportunities

```python
# Get all opportunities
opportunities = client.get_opportunities(page=1, size=20)

# Get a specific opportunity
opp = client.get_opportunity_by_id("168180")
if opp:
    print(f"Opportunity: {opp['Name']}")
    print(f"Value: {opp.get('Value', 0)}")
```

### Fetch Persons (Contacts)

```python
# Get all persons
persons = client.get_persons(page=1, size=20)

# Get persons in a specific organisation
org_persons = client.get_persons(org_id="2", page=1, size=20)

for person in org_persons:
    print(f"{person['PersonFirstName']} {person['PersonLastName']}")
    print(f"Email: {person.get('PersonEmail', 'N/A')}")
```

### Create a Person

```python
new_person = client.create_person({
    "FirstName": "John",
    "LastName": "Doe",
    "Email": "john.doe@example.com",
    "Phone": "+45 12 34 56 78",
    "OrganisationId": "12345"
})
```

### Custom API Request

For endpoints not yet implemented, use the generic `_make_request` method:

```python
result = client._make_request(
    "GET",
    "/CustomEndpoint",
    params={"filter": "active"}
)
```

## Project Structure

```
.
├── test_webcrm.py          # Main API clien
├── README.md               # This file
├── .gitignore              # Git ignore rules
├── .env                    # Environment variables (not in repo)
└── requirements.txt        # Python dependencies
```

## API Methods Available

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `get_organisations(page, size)` | GET `/Organisations` | List organisations |
| `get_organisation_by_id(id)` | GET `/Organisations/{id}` | Get single organisation |
| `get_opportunities(page, size)` | GET `/Opportunities` | List opportunities |
| `get_opportunity_by_id(id)` | GET `/Opportunities/{id}` | Get single opportunity |
| `get_persons(org_id, page, size)` | GET `/Persons` or `/Organisations/{id}/Persons` | List persons |
| `create_person(data)` | POST `/Persons` | Create new person |

## Adding New Endpoints

To add a new endpoint, add a method to the `WebCRMClient` class:

```python
def get_tasks(self, page: int = 1, size: int = 20) -> Optional[list]:
    """Fetch tasks"""
    result = self._make_request("GET", "/Tasks", params={"page": page, "size": size})
    if result:
        print(f"✅ Found {len(result)} tasks")
    return result
```

## Debugging

Enable detailed logging by setting `debug=True` (default):

```python
client = WebCRMClient(BASE_URL, TOKEN, debug=True)
```

This will print:
- 📤 Request details (method, URL)
- 📥 Response status and preview
- ℹ️ Sample data from responses
- ❌ Error details and suggestions

## Common Issues & Solutions

### ❌ "Missing WEBCRM_BASE_URL or WEBCRM_TOKEN"
**Cause:** `.env` file not found or variables not loaded

**Solution:**
1. Ensure `.env` file exists in the project root (same folder as `test_webcrm.py`)
2. Check credentials have no extra spaces or quotes
3. Verify file is named exactly `.env` (not `.env.txt`)

### ❌ "401 Unauthorized" when calling API
**Cause:** authCode (token from .env) expired or invalid

**Solution:**
1. Generate a new authCode in WebCRM Settings → API → Generate new token
2. Update `.env` file with new token:
   ```
   WEBCRM_TOKEN=your-new-token-here
   ```
3. Run script again (authentication is automatic)

**Note:** The code automatically exchanges your authCode for an AccessToken - you don't need to do this manually!

### ❌ "404 Not Found" for endpoint
**Cause:** Incorrect endpoint path or resource doesn't exist

**Solution:**
- Check endpoint path matches [WebCRM API docs](https://api.webcrm.com/docs)
- Verify resource ID exists (e.g., check organisation ID is correct)
- Ensure spelling is correct (case-sensitive)

### ❌ Token still reads old value after updating `.env`
**Cause:** Environment variables cached in Python session

**Solution:**
- Restart your Python terminal/IDE
- Code already includes `load_dotenv(override=True)` to force reload
- Alternatively, delete any `.pyc` files or `__pycache__` folders

### ❌ Connection Timeout
**Cause:** Network issues or slow API

**Solution:**
- Check internet connection
- Verify `WEBCRM_BASE_URL=https://api.webcrm.com` (no trailing slash)
- Try a smaller page size (e.g., `size=5` instead of `size=20`)

## Next Steps

- Modify test cases in `test_webcrm.py` to match your use case
- Add custom endpoints as needed
- Integrate with CI/CD pipelines
- Build more complex test scenarios

## Resources

- [WebCRM API Documentation](https://api.webcrm.com/docs)
- [Requests Library Docs](https://requests.readthedocs.io/)
- [Python Dotenv](https://python-dotenv.readthedocs.io/)

## License

This project is for testing and development purposes.

