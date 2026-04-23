import os
import requests
from dotenv import load_dotenv

load_dotenv()

wp_url = os.getenv("WP_URL_SITE2")
wp_user = os.getenv("WP_USER_SITE2")
wp_app_password = os.getenv("WP_APP_PASSWORD_SITE2")

print(f"🔍 Testing connection to Site 2: {wp_url}")

if not wp_url or not wp_user or not wp_app_password:
    print("❌ ERROR: Missing credentials in .env file. Check your variable names!")
else:
    # We use a simple GET request to see if WordPress accepts our credentials
    wp_api_url = f"{wp_url}/wp-json/wp/v2/posts"
    response = requests.get(wp_api_url, auth=(wp_user, wp_app_password))

    if response.status_code == 200:
        print("✅ SUCCESS! Python is successfully communicating with Site 2.")
    else:
        print(f"❌ FAILED. Error {response.status_code}: {response.text}")