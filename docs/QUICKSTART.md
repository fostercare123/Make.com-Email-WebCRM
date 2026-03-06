# 🚀 Quick Start Guide - WebCRM API Tester

Get started with the WebCRM API in 5 minutes!

## Step 1: Get Your API Token

1. Log into your WebCRM account
2. Go to **Settings** → **API**
3. Click **"Generate new token"**
4. Copy the token (it looks like: `a1b2c3d4-e5f6-7890-abcd-1234567890ef`)

## Step 2: Create Your `.env` File

Copy the example file and add your credentials:

```powershell
# Copy the example file
copy .env.example .env
```

Then edit `.env` and replace `your-api-token-here` with the token you copied!

```
WEBCRM_BASE_URL=https://api.webcrm.com
WEBCRM_TOKEN=your-token-here
```

Replace `your-token-here` with the token you copied!

## Step 3: Install Dependencies

Open a terminal in your project folder and run:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

## Step 4: Run a Test!

Run the test script to see if everything works:

```powershell
python test_webcrm.py
```

You should see:
```
🔗 Testing API connection...
✅ Found 5 organisations
✅ Connected to WebCRM!
```

## Step 5: Use in Your Own Code

Now you can use the WebCRM API in your own scripts:

```python
from test_webcrm import WebCRMClient
import os
from dotenv import load_dotenv

# Load credentials
load_dotenv()

# Create client (authentication is automatic!)
client = WebCRMClient(
    os.getenv("WEBCRM_BASE_URL"),
    os.getenv("WEBCRM_TOKEN"),
    debug=False  # Set to True for detailed output
)

# Get your companies
companies = client.get_organisations(page=1, size=20)
for company in companies:
    print(f"{company['OrganisationName']}")
```

---

## 🎯 What's Next?

- **See all available methods:** Check [README.md](README.md)
- **Need help?** See the troubleshooting section in [README.md](README.md)
- **Want to add more endpoints?** See "Adding New Endpoints" in [README.md](README.md)

---

## 🔑 How Authentication Works (Behind the Scenes)

You don't need to worry about this - it happens automatically! But if you're curious:

1. **You provide:** An `authCode` token (from WebCRM Settings → API)
2. **The code does:** Exchanges your authCode for a temporary `AccessToken` (valid for 1 hour)
3. **The code uses:** The AccessToken as a Bearer token for all API calls
4. **The result:** You just call methods and they work! 🎉

Every API call automatically gets a fresh AccessToken, so you never have to worry about expiration.

---

## Make.com Scenario: Email → webCRM (Create If New)

Use this blueprint when you want incoming "Request a Quote" emails to create new Company + Contact in webCRM only when the email does not already exist.

1. Import [Request-Quote-WebCRM-MERGED.blueprint.json](Request-Quote-WebCRM-MERGED.blueprint.json) into Make.com.
2. Configure the Email module connection for info@eilersen.com.
3. Create a Make.com Data Store record with key `authcode` containing your webCRM auth code.
4. In the HTTP ApiLogin module, verify `authCode={{datastore.authcode}}`.
5. Run once with a test email body in this exact format:

```text
Full Name: Jane Doe
Email Address: jane@example.com
Phone: +45 11 22 33 44
Company Name: Example A/S
Country: Denmark
```

Expected behavior:
- If `/Persons/Search` finds email matches, scenario skips create.
- If no matches are found, scenario posts to `/Organisations` and then `/Persons` to create Company + Contact.
