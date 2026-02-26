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