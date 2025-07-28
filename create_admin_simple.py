#!/usr/bin/env python3
"""
Simple script to create an admin user with default credentials.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import SessionLocal
from models import User
from utils.auth_utils import get_password_hash

def create_admin_user():
    """Create an admin user with default credentials."""
    db = SessionLocal()
    
    try:
        username = "admin"
        password = "admin123"
        email = "admin@example.com"
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"User '{username}' already exists!")
            return False
        
        # Create new admin user
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role="admin"  # Use 'role' field instead of 'is_admin'
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Admin user '{username}' created successfully!")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Email: {new_user.email}")
        print(f"Role: {new_user.role}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=== Creating Default Admin User ===\n")
    
    success = create_admin_user()
    
    if success:
        print(f"\n🎉 Login credentials:")
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"\nYou can now log in at: http://localhost:8501")
    else:
        print("\n❌ Failed to create admin user.")
        sys.exit(1) 