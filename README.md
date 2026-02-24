# WebCRM API Tester

A lightweight Python utility for testing WebCRM API endpoints directly in code. Think of it as **Postman in Python** — perfect for automating API tests, debugging requests, and validating integrations.

## Features

✅ Simple API client for testing WebCRM endpoints  
✅ Built-in debugging output with request/response details  
✅ Support for GET, POST, PUT, DELETE methods  
✅ Clean, organized code with reusable methods  
✅ Error handling and timeout management  
✅ Environment-based configuration (.env)

## Prerequisites

- Python 3.8+
- `requests` library
- `python-dotenv` library
- Valid WebCRM API token and base URL

## Setup

### 1. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate

# Activate it (macOS/Linux)
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests python-dotenv
```

### 3. Create a `.env` File

Create a `.env` file in the project root with your WebCRM credentials:

```env
WEBCRM_BASE_URL=https://api.webcrm.com
WEBCRM_TOKEN=your-36-character-token-here
```

⚠️ **Never commit the `.env` file to version control!** It's already in `.gitignore`.

### 4. Run Tests

```bash
python test_webcrm.py
```

## Usage Examples

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
client.test_connection()
```

### Fetch Organisations

```python
# Get all organisations
organisations = client.get_organisations(page=1, size=20)

# Get a specific organisation
org = client.get_organisation_by_id("12345")
```

### Fetch Opportunities

```python
# Get all opportunities
opportunities = client.get_opportunities(page=1, size=20)

# Get a specific opportunity
opp = client.get_opportunity_by_id("168180")
```

### Fetch Persons

```python
# Get all persons
persons = client.get_persons(page=1, size=20)

# Get persons in an organisation
org_persons = client.get_persons(org_id="12345", page=1, size=20)
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
├── test_webcrm.py          # Main API client
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

## Common Issues

### ❌ "Missing WEBCRM_BASE_URL or WEBCRM_TOKEN"
- Ensure `.env` file exists in the project root
- Check credentials are correct (no extra spaces)
- Verify token hasn't expired

### ❌ "401 Unauthorized"
- Token may have expired → regenerate in WebCRM
- Check token format (should be Bearer token)
- Verify API permissions in WebCRM

### ❌ "404 Not Found"
- Endpoint path may be incorrect
- Resource ID may not exist
- Check API documentation for correct paths

### ❌ Connection Timeout
- Check internet connection
- Verify BASE_URL is correct
- Try increasing timeout value in code

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

