#!/usr/bin/env python3
"""
Create a single test user for Stripe testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from models import User, Store
from utils.auth_utils import get_password_hash
from sqlalchemy.orm import sessionmaker

def create_stripe_test_user():
    """Create a single test user for Stripe testing"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.username == "stripe_test").first()
        if existing_user:
            print("✅ Test user already exists!")
            print(f"Username: {existing_user.username}")
            print(f"Email: {existing_user.email}")
            print(f"Role: {existing_user.role}")
            return
        
        # Get or create a test store
        test_store = db.query(Store).filter(Store.id == 1).first()
        if not test_store:
            print("❌ No store found. Please run init_db.py first to create stores.")
            return
        
        # Create new test user
        test_user = User(
            username="stripe_test",
            email="stripe_test@example.com",
            hashed_password=get_password_hash("testpass123"),
            role="employee",  # Start as employee to test billing flow
            store_id=test_store.id  # Assign to existing store
        )
        
        db.add(test_user)
        db.commit()
        print("✅ Test user created successfully!")
        print("Username: stripe_test")
        print("Email: stripe_test@example.com")
        print("Password: testpass123")
        print("Role: employee (will need to subscribe)")
        print(f"Store: {test_store.name} ({test_store.location})")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_stripe_test_user() 