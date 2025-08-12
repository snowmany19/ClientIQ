#!/usr/bin/env python3
"""
Create demo users for the ContractGuard.ai platform demo environment.
This script creates sample users with different roles for demonstration purposes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db
from backend.models import User, Workspace
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
            print("Analyst User:")
            print("  Email: analyst@demo.com")
            print("  Password: demo123")
            print("  Role: Analyst (contract analysis)")
            print()
            print("Viewer User:")
            print("  Email: viewer@demo.com")
            print("  Password: demo123")
            print("  Role: Viewer (read-only access)")
            print()
            print("Super Admin:")
            print("  Email: superadmin@demo.com")
            print("  Password: demo123")
            print("  Role: Super Admin (system-wide access)")
            return
        
        # Create demo workspace
        demo_workspace = Workspace(
            name="Demo Workspace",
            company_name="Demo Company Inc.",
            contact_email="demo@company.com",
            contact_phone="555-0123"
        )
        db.add(demo_workspace)
        db.commit()
        db.refresh(demo_workspace)
        
        # Create demo admin user
        demo_admin = User(
            username="admin",
            email="admin@demo.com",
            hashed_password=hash_password("demo123"),
            first_name="Demo",
            last_name="Admin",
            role="admin",
            workspace_id=demo_workspace.id,
            company_name="Demo Company Inc.",
            phone="555-0123"
        )
        db.add(demo_admin)
        
        # Create demo analyst user
        demo_analyst = User(
            username="analyst",
            email="analyst@demo.com",
            hashed_password=hash_password("demo123"),
            first_name="Demo",
            last_name="Analyst",
            role="analyst",
            workspace_id=demo_workspace.id,
            company_name="Demo Company Inc.",
            phone="555-0124"
        )
        db.add(demo_analyst)
        
        # Create demo viewer user
        demo_viewer = User(
            username="viewer",
            email="viewer@demo.com",
            hashed_password=hash_password("demo123"),
            first_name="Demo",
            last_name="Viewer",
            role="viewer",
            workspace_id=demo_workspace.id,
            company_name="Demo Company Inc.",
            phone="555-0125"
        )
        db.add(demo_viewer)
        
        # Create demo super admin user
        demo_super_admin = User(
            username="superadmin",
            email="superadmin@demo.com",
            hashed_password=hash_password("demo123"),
            first_name="Demo",
            last_name="Super Admin",
            role="super_admin",
            workspace_id=demo_workspace.id,
            company_name="Demo Company Inc.",
            phone="555-0126"
        )
        db.add(demo_super_admin)
        
        db.commit()
        
        print("✅ Demo users created successfully!")
        print("\nDemo Account Credentials:")
        print("=" * 40)
        print("Admin User:")
        print("  Email: admin@demo.com")
        print("  Password: demo123")
        print("  Role: Admin (full access)")
        print()
        print("Analyst User:")
        print("  Email: analyst@demo.com")
        print("  Password: demo123")
        print("  Role: Analyst (contract analysis)")
        print()
        print("Viewer User:")
        print("  Email: viewer@demo.com")
        print("  Password: demo123")
        print("  Role: Viewer (read-only access)")
        print()
        print("Super Admin:")
        print("  Email: superadmin@demo.com")
        print("  Password: demo123")
        print("  Role: Super Admin (system-wide access)")
        print()
        print("Demo Workspace ID:", demo_workspace.id)
        
    except Exception as e:
        print(f"❌ Error creating demo users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_users() 