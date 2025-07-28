#!/usr/bin/env python3
"""
Script to create an admin user for the HOA Log application.
Run this script to create a new admin user in the database.
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

def create_admin_user(username: str, password: str, email: str = None):
    """Create an admin user in the database."""
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"User '{username}' already exists!")
            return False
        
        # Create new admin user
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email or f"{username}@example.com",
            hashed_password=hashed_password,
            is_admin=True,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ Admin user '{username}' created successfully!")
        print(f"Username: {username}")
        print(f"Email: {new_user.email}")
        print(f"Admin: {new_user.is_admin}")
        print(f"Active: {new_user.is_active}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=== HOA Log Admin User Creator ===\n")
    
    # Default admin credentials
    default_username = "admin"
    default_password = "admin123"
    
    print(f"Creating admin user with default credentials:")
    print(f"Username: {default_username}")
    print(f"Password: {default_password}")
    print()
    
    # You can modify these values or make them interactive
    username = input(f"Enter username (default: {default_username}): ").strip() or default_username
    password = input(f"Enter password (default: {default_password}): ").strip() or default_password
    email = input("Enter email (optional): ").strip() or None
    
    print(f"\nCreating admin user '{username}'...")
    
    success = create_admin_user(username, password, email)
    
    if success:
        print(f"\n🎉 Login credentials:")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"\nYou can now log in at: http://localhost:8501")
    else:
        print("\n❌ Failed to create admin user. Please check the error message above.")
        sys.exit(1) 