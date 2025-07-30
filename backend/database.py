# Database connection logic
# database.py
# ✅ Handles database connection, engine, session creation

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# 🔁 Load environment variables
load_dotenv()

# 🧠 Get DB URL (PostgreSQL preferred)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./a_incident.db")

# 🛠 Engine setup with connection pooling for production
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Production-ready PostgreSQL configuration with connection pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,  # Number of connections to maintain
        max_overflow=30,  # Additional connections when pool is full
        pool_pre_ping=True,  # Validate connections before use
        pool_recycle=3600,  # Recycle connections every hour
        pool_timeout=30,  # Timeout for getting connection from pool
        echo=False,  # Set to True for SQL query logging in development
    )

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
