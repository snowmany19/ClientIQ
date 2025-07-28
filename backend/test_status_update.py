#!/usr/bin/env python3
"""
Test script to debug the status update functionality
"""

import requests
import json
from database import SessionLocal
from models import User, Violation
from utils.auth_utils import create_access_token

def test_status_update():
    """Test the status update endpoint directly."""
    
    # Get a test user and violation
    db = SessionLocal()
    
    # Get a user with proper role
    user = db.query(User).filter(User.role.in_(['admin', 'hoa_board', 'inspector'])).first()
    if not user:
        print("No users with proper roles found")
        return
    
    # Get a violation
    violation = db.query(Violation).first()
    if not violation:
        print("No violations found")
        return
    
    print(f"Testing with user: {user.username} (role: {user.role})")
    print(f"Testing violation: {violation.id} (status: {violation.status})")
    
    # Create access token
    token = create_access_token(data={"sub": user.username})
    
    # Test the status update
    url = f"http://localhost:8000/api/violations/{violation.id}/status?new_status=resolved"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.put(url, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Status update successful!")
        else:
            print("❌ Status update failed!")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    db.close()

if __name__ == "__main__":
    test_status_update() 