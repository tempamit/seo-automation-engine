import os
import requests
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

# The WordPress REST API endpoint for posts
wp_api_url = f"{WP_URL}/wp-json/wp/v2/posts"

# The test payload
data = {
    "title": "Engine Diagnostics: WP API Connection Test",
    "content": "<p>If you see this draft, the Python engine is successfully communicating with your live Hostinger site. The pipeline is open.</p>",
    "status": "draft"
}

print(f"Pinging {WP_URL}...")

response = requests.post(
    wp_api_url,
    json=data,
    auth=(WP_USER, WP_APP_PASSWORD)
)

if response.status_code == 201:
    print("✅ Success! Check your WordPress Admin -> Posts (Drafts).")
else:
    print(f"❌ Failed. Error {response.status_code}: {response.text}")