# Database connection logic
# database.py
# ✅ Handles database connection, engine, session creation

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 🔁 Load environment variables
load_dotenv()

# 🧠 Get DB URL (PostgreSQL preferred)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./incidentiq.db")

# 🛠 Engine setup
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# 🧱 Base for ORM models
Base = declarative_base()

# ⚙️ Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 📦 Dependency for DB session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
