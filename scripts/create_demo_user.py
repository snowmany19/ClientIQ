#!/usr/bin/env python3
"""
Create demo users for the HOA-Log platform demo environment.
This script creates sample users with different roles for demonstration purposes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db
from backend.models import User, HOA
from backend.utils.auth_utils import hash_password
from sqlalchemy.orm import Session

def create_demo_users():
    """Create demo users for the platform."""
    db = next(get_db())
    
    try:
        # Check if demo users already exist
        existing_admin = db.query(User).filter(User.email == "admin@demo.com").first()
        if existing_admin:
            print("✅ Demo users already exist!")
            print("\nDemo Account Credentials:")
            print("=" * 40)
            print("Admin User:")
            print("  Email: admin@demo.com")
            print("  Password: demo123")
            print("  Role: Admin (full access)")
            print()
            print("HOA Board Member:")
            print("  Email: board@demo.com")
            print("  Password: demo123")
            print("  Role: HOA Board (management access)")
            print()
            print("Inspector:")
            print("  Email: inspector@demo.com")
            print("  Password: demo123")
            print("  Role: Inspector (violation capture)")
            print()
            print("Resident:")
            print("  Email: resident@demo.com")
            print("  Password: demo123")
            print("  Role: Resident (portal access)")
            return
        
        # Create demo HOA
        demo_hoa = HOA(
            name="Demo HOA",
            address="123 Demo Street, Demo City, DC 12345",
            contact_email="demo@hoa.com",
            contact_phone="555-0123"
        )
        db.add(demo_hoa)
        db.commit()
        db.refresh(demo_hoa)
        
        # Create demo admin user
        demo_admin = User(
            username="demo_admin",
            email="admin@demo.com",
            password_hash=hash_password("demo123"),
            role="admin",
            is_active=True,
            subscription_status="active"
        )
        db.add(demo_admin)
        
        # Create demo HOA board member
        demo_board = User(
            username="demo_board",
            email="board@demo.com",
            password_hash=hash_password("demo123"),
            role="hoa_board",
            hoa_id=demo_hoa.id,
            is_active=True,
            subscription_status="active"
        )
        db.add(demo_board)
        
        # Create demo inspector
        demo_inspector = User(
            username="demo_inspector",
            email="inspector@demo.com",
            password_hash=hash_password("demo123"),
            role="inspector",
            hoa_id=demo_hoa.id,
            is_active=True,
            subscription_status="active"
        )
        db.add(demo_inspector)
        
        # Create demo resident
        demo_resident = User(
            username="demo_resident",
            email="resident@demo.com",
            password_hash=hash_password("demo123"),
            role="resident",
            hoa_id=demo_hoa.id,
            is_active=True,
            subscription_status="active"
        )
        db.add(demo_resident)
        
        db.commit()
        
        print("✅ Demo users created successfully!")
        print("\nDemo Account Credentials:")
        print("=" * 40)
        print("Admin User:")
        print("  Email: admin@demo.com")
        print("  Password: demo123")
        print("  Role: Admin (full access)")
        print()
        print("HOA Board Member:")
        print("  Email: board@demo.com")
        print("  Password: demo123")
        print("  Role: HOA Board (management access)")
        print()
        print("Inspector:")
        print("  Email: inspector@demo.com")
        print("  Password: demo123")
        print("  Role: Inspector (violation capture)")
        print()
        print("Resident:")
        print("  Email: resident@demo.com")
        print("  Password: demo123")
        print("  Role: Resident (portal access)")
        print()
        print("Demo HOA ID:", demo_hoa.id)
        
    except Exception as e:
        print(f"❌ Error creating demo users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_users() 