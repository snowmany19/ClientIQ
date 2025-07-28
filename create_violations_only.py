#!/usr/bin/env python3
"""
Simple script to add violations with predefined tags to existing HOAs and residents.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import SessionLocal
from models import User, HOA, Resident
from sqlalchemy import text

# Predefined tags for HOA violations (matching backend FIXED_TAGS)
PREDEFINED_TAGS = [
    "Landscaping", "Trash", "Parking", "Exterior Maintenance", "Noise",
    "Pet Violation", "Architectural", "Pool/Spa", "Vehicle Storage",
    "Holiday Decorations", "Other", "Safety Hazard"
]

def create_violations():
    """Create violations with predefined tags for existing HOAs and residents."""
    db = SessionLocal()
    
    try:
        # Get the admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("❌ Admin user not found!")
            return False
        
        # Get existing HOAs
        hoas = db.query(HOA).all()
        if not hoas:
            print("❌ No HOAs found!")
            return False
        
        # Get existing residents
        residents = db.query(Resident).all()
        if not residents:
            print("❌ No residents found!")
            return False
        
        print(f"✅ Found {len(hoas)} HOAs and {len(residents)} residents")
        
        # Create sample violations using predefined tags
        violation_scenarios = [
            {
                "description": "Vehicle parked in unauthorized area blocking driveway",
                "summary": "Parking violation reported for unauthorized vehicle placement",
                "tags": ["Parking"]
            },
            {
                "description": "Excessive noise from party after 10 PM quiet hours",
                "summary": "Noise complaint filed for late night disturbance",
                "tags": ["Noise"]
            },
            {
                "description": "Overgrown bushes and unkempt lawn affecting curb appeal",
                "summary": "Landscaping maintenance issue requiring attention",
                "tags": ["Landscaping"]
            },
            {
                "description": "Dog not on leash in common areas, owner not present",
                "summary": "Pet policy violation for unleashed animal in shared spaces",
                "tags": ["Pet Violation"]
            },
            {
                "description": "Trash bins left out past collection time for 3 days",
                "summary": "Trash disposal policy violation requiring cleanup",
                "tags": ["Trash"]
            },
            {
                "description": "Recreational vehicle stored in driveway exceeding 48 hours",
                "summary": "Vehicle storage policy violation for extended parking",
                "tags": ["Vehicle Storage"]
            },
            {
                "description": "Unauthorized exterior paint color change without approval",
                "summary": "Architectural modification without proper authorization",
                "tags": ["Architectural"]
            },
            {
                "description": "Pool area not properly maintained, safety concerns",
                "summary": "Pool/Spa maintenance and safety issue reported",
                "tags": ["Pool/Spa"]
            },
            {
                "description": "Holiday decorations still displayed after allowed period",
                "summary": "Holiday decoration policy violation for extended display",
                "tags": ["Holiday Decorations"]
            },
            {
                "description": "Broken fence post creating potential safety hazard",
                "summary": "Safety hazard identified requiring immediate attention",
                "tags": ["Safety Hazard"]
            },
            {
                "description": "Exterior maintenance overdue, peeling paint and damaged siding",
                "summary": "Exterior maintenance violation requiring property upkeep",
                "tags": ["Exterior Maintenance"]
            }
        ]
        
        # Create violations for each HOA
        violation_number = 1000
        for hoa in hoas:
            # Get residents for this HOA
            hoa_residents = [r for r in residents if r.hoa_id == hoa.id]
            
            if not hoa_residents:
                continue
            
            # Create 5-8 violations per HOA
            num_violations = random.randint(5, 8)
            for i in range(num_violations):
                resident = random.choice(hoa_residents)
                scenario = random.choice(violation_scenarios)
                
                # Create violation with random dates in the last 30 days
                days_ago = random.randint(0, 30)
                timestamp = datetime.utcnow() - timedelta(days=days_ago)
                
                # Create violation using raw SQL
                violation_data = {
                    'violation_number': violation_number,
                    'description': f"{scenario['description']} at {resident.address}.",
                    'summary': f"{scenario['summary']} for {resident.name}",
                    'tags': ", ".join(scenario['tags']),
                    'timestamp': timestamp,
                    'hoa_name': f"HOA #{hoa.id:03d}",
                    'address': resident.address,
                    'location': "Property",
                    'offender': resident.name,
                    'status': random.choice(["open", "under_review", "resolved"]),
                    'repeat_offender_score': random.randint(1, 5),
                    'user_id': admin_user.id
                }
                
                sql = text("""
                    INSERT INTO violations (
                        violation_number, description, summary, tags, timestamp,
                        hoa_name, address, location, offender, status,
                        repeat_offender_score, user_id
                    ) VALUES (
                        :violation_number, :description, :summary, :tags, :timestamp,
                        :hoa_name, :address, :location, :offender, :status,
                        :repeat_offender_score, :user_id
                    )
                """)
                
                db.execute(sql, violation_data)
                print(f"✅ Created violation #{violation_number}: {scenario['tags'][0]} for {resident.name} in {hoa.name}")
                violation_number += 1
        
        db.commit()
        
        print(f"\n🎉 Successfully created {violation_number - 1000} violations with predefined tags!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating violations: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=== Creating Violations with Predefined Tags ===\n")
    
    success = create_violations()
    
    if success:
        print(f"\n🎉 You can now test the system with:")
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"URL: http://localhost:8501")
        print(f"\nThe system now has violations with proper predefined tags!")
    else:
        print("\n❌ Failed to create violations.")
        sys.exit(1) 