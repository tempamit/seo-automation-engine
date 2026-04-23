from database import engine, Base
import models

print("Connecting to live Hostinger database...")
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Success! Database schema generated.")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("Check if your IP is whitelisted in Hostinger Remote MySQL.")