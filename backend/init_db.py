# backend/init_db.py
# Database initialization script for CivicLogHOA - HOA Violation Management Platform

import os
import sys
from sqlalchemy.orm import sessionmaker
from database import engine, Base
from models import User, HOA
from utils.auth_utils import get_password_hash
from core.config import get_settings

# Get settings
settings = get_settings()

# Use environment DATABASE_URL or default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./civicloghoa.db")

print("🗄️ Initializing CivicLogHOA - HOA Violation Management Platform database...")

# Create tables
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Create test HOAs
    print("🏘️ Creating test HOAs...")
    hoas = [
        HOA(id=1, name="Downtown HOA", location="123 Main St, Downtown", contact_email="admin@downtownhoa.com", contact_phone="555-0101"),
        HOA(id=66, name="Mall HOA", location="456 Shopping Ave, Mall", contact_email="admin@mallhoa.com", contact_phone="555-0666"),
    ]
    
    for hoa in hoas:
        db.add(hoa)
    db.commit()
    print(f"✅ Created {len(hoas)} HOAs")

    # Create test users
    print("👥 Creating test users...")
    users_data = [
        {
            "username": "admin",
            "password": "test123",
            "email": "admin@civicloghoa.com",
            "role": "admin",
            "hoa_id": None,  # Admin has no HOA restriction
        },
        {
            "username": "johndoe",
            "password": "test123", 
            "email": "john@civicloghoa.com",
            "role": "inspector",
            "hoa_id": 1,  # Assigned to HOA #001
        },
        {
            "username": "manager1",
            "password": "test123",
            "email": "manager@civicloghoa.com", 
            "role": "hoa_board",
            "hoa_id": 66,  # Assigned to HOA #066
        },
        {
            "username": "employee1",
            "password": "test123",
            "email": "employee@civicloghoa.com",
            "role": "inspector", 
            "hoa_id": 1,  # Assigned to HOA #001
        },
        {
            "username": "Jaclyn1",
            "password": "test123",
            "email": "jaclyn@civicloghoa.com",
            "role": "inspector",
            "hoa_id": 66,  # Assigned to HOA #066
        }
    ]

    for user_data in users_data:
        hashed_password = get_password_hash(user_data["password"])
        user = User(
            username=user_data["username"],
            hashed_password=hashed_password,
            email=user_data["email"],
            role=user_data["role"],
            hoa_id=user_data["hoa_id"],
        )
        db.add(user)
    
    db.commit()
    print(f"✅ Created {len(users_data)} users")

    # Display summary
    print("\n📊 Database Summary:")
    print("=" * 50)
    
    hoas = db.query(HOA).all()
    print(f"🏘️ HOAs ({len(hoas)}):")
    for hoa in hoas:
        print(f"  - HOA #{hoa.id:03d}: {hoa.name} - {hoa.location}")
    
    print(f"\n👥 Users ({len(users_data)}):")
    for user in db.query(User).all():
        hoa_info = "All Locations" if user.hoa_id is None else f"HOA #{user.hoa_id:03d}"
        print(f"  - {user.username} ({user.role}) - {hoa_info}")
    
    print("\n🔑 Test Login Credentials:")
    print("=" * 50)
    print("Admin:     username=admin, password=test123 (All HOAs)")
    print("John Doe:  username=johndoe, password=test123 (HOA #001)")
    print("Manager:   username=manager1, password=test123 (HOA #066)")
    print("Employee:  username=employee1, password=test123 (HOA #001)")
    print("Jaclyn1:   username=Jaclyn1, password=test123 (HOA #066)")

except Exception as e:
    print(f"❌ Error initializing database: {e}")
    db.rollback()
finally:
    db.close()

print("\n✅ Database initialization complete!")
