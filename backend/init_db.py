# backend/init_db.py
# Database initialization script for ContractGuard - AI Contract Review Platform

import os
import sys
from sqlalchemy.orm import sessionmaker
from database import engine, Base
from models import User
from utils.auth_utils import get_password_hash
from core.config import get_settings

# Get settings
settings = get_settings()

# Use environment DATABASE_URL or default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./contractguard.db")

print("🗄️ Initializing ContractGuard - AI Contract Review Platform database...")

# Create tables
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Create test users
    print("👥 Creating test users...")
    users_data = [
        {
            "username": "admin",
            "password": "test123",
            "email": "admin@contractguard.ai",
            "role": "admin",
        },
        {
            "username": "johndoe",
            "password": "test123", 
            "email": "john@contractguard.ai",
            "role": "analyst",
        },
        {
            "username": "manager1",
            "password": "test123",
            "email": "manager@contractguard.ai", 
            "role": "admin",
        },
        {
            "username": "employee1",
            "password": "test123",
            "email": "employee@contractguard.ai", 
            "role": "analyst", 
        },
        {
            "username": "Jaclyn1",
            "password": "test123",
            "email": "jaclyn@contractguard.ai",
            "role": "analyst",
        }
    ]

    for user_data in users_data:
        hashed_password = get_password_hash(user_data["password"])
        user = User(
            username=user_data["username"],
            hashed_password=hashed_password,
            email=user_data["email"],
            role=user_data["role"],
        )
        db.add(user)
    
    db.commit()
    print(f"✅ Created {len(users_data)} users")

    # Display summary
    print("\n📊 Database Summary:")
    print("=" * 50)
    
    print(f"\n👥 Users ({len(users_data)}):")
    for user in db.query(User).all():
        print(f"  - {user.username} ({user.role})")
    
    print("\n🔑 Test Login Credentials:")
    print("=" * 50)
    print("Admin:     username=admin, password=test123")
    print("John Doe:  username=johndoe, password=test123")
    print("Manager:   username=manager1, password=test123")
    print("Employee:  username=employee1, password=test123")
    print("Jaclyn1:   username=Jaclyn1, password=test123")

except Exception as e:
    print(f"❌ Error initializing database: {e}")
    db.rollback()
finally:
    db.close()

print("\n✅ Database initialization complete!")
