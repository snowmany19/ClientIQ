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
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./contractguard.db")

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
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# 🔄 Database health check
def check_database_health():
    """Check if database is accessible and healthy."""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False

# 🚨 Database connection retry logic
def get_db_with_retry(max_retries: int = 3, retry_delay: float = 1.0):
    """Get database session with retry logic for transient failures."""
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Test connection
            db.execute("SELECT 1")
            return db
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            import time
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
