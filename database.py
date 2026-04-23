import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# 1. Load credentials from the .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is missing! Check your .env file.")

# 2. Initialize the Engine with Hostinger-specific timeout protections
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Pings the connection to check if Hostinger dropped it
    pool_recycle=60      # Automatically recycles connections older than 60 seconds
)

# 3. Setup the Session and Base Model
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()