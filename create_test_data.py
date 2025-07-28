#!/usr/bin/env python3
"""
Script to create test HOAs and sample data for testing the HOA Log application.
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
from models import User, HOA, Resident, Violation

def create_test_data():
    """Create test HOAs and sample data."""
    db = SessionLocal()
    
    try:
        # Get the admin user
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("❌ Admin user not found! Please create admin user first.")
            return False
        
        print("✅ Found admin user:", admin_user.username)
        
        # Create 3 test HOAs
        test_hoas = [
            {
                "name": "Sunset Gardens HOA",
                "location": "123 Sunset Blvd, Beverly Hills, CA 90210",
                "contact_email": "board@sunsetgardens.com",
                "contact_phone": "(310) 555-0101"
            },
            {
                "name": "Palm Springs Estates",
                "location": "456 Palm Drive, Palm Springs, CA 92262",
                "contact_email": "info@palmspringsestates.com",
                "contact_phone": "(760) 555-0202"
            },
            {
                "name": "Marina Bay Condominiums",
                "location": "789 Harbor Way, Newport Beach, CA 92660",
                "contact_email": "management@marinabay.com",
                "contact_phone": "(949) 555-0303"
            }
        ]
        
        created_hoas = []
        for hoa_data in test_hoas:
            # Check if HOA already exists
            existing_hoa = db.query(HOA).filter(HOA.name == hoa_data["name"]).first()
            if existing_hoa:
                print(f"HOA '{hoa_data['name']}' already exists!")
                created_hoas.append(existing_hoa)
                continue
            
            hoa = HOA(**hoa_data)
            db.add(hoa)
            db.flush()  # Get the ID
            created_hoas.append(hoa)
            print(f"✅ Created HOA: {hoa.name}")
        
        # Create test residents for each HOA
        test_residents = [
            # Sunset Gardens residents
            {"name": "John Smith", "address": "101 Sunset Gardens", "email": "john.smith@email.com", "phone": "(310) 555-1001"},
            {"name": "Sarah Johnson", "address": "102 Sunset Gardens", "email": "sarah.j@email.com", "phone": "(310) 555-1002"},
            {"name": "Mike Davis", "address": "103 Sunset Gardens", "email": "mike.davis@email.com", "phone": "(310) 555-1003"},
            
            # Palm Springs residents
            {"name": "Lisa Wilson", "address": "201 Palm Springs Estates", "email": "lisa.w@email.com", "phone": "(760) 555-2001"},
            {"name": "Robert Brown", "address": "202 Palm Springs Estates", "email": "robert.b@email.com", "phone": "(760) 555-2002"},
            {"name": "Jennifer Garcia", "address": "203 Palm Springs Estates", "email": "jen.garcia@email.com", "phone": "(760) 555-2003"},
            
            # Marina Bay residents
            {"name": "David Martinez", "address": "301 Marina Bay", "email": "david.m@email.com", "phone": "(949) 555-3001"},
            {"name": "Amanda Taylor", "address": "302 Marina Bay", "email": "amanda.t@email.com", "phone": "(949) 555-3002"},
            {"name": "Chris Anderson", "address": "303 Marina Bay", "email": "chris.a@email.com", "phone": "(949) 555-3003"},
        ]
        
        created_residents = []
        for i, resident_data in enumerate(test_residents):
            hoa_index = i // 3  # Assign 3 residents per HOA
            resident_data["hoa_id"] = created_hoas[hoa_index].id
            
            # Check if resident already exists
            existing_resident = db.query(Resident).filter(
                Resident.name == resident_data["name"],
                Resident.hoa_id == resident_data["hoa_id"]
            ).first()
            if existing_resident:
                print(f"Resident '{resident_data['name']}' already exists!")
                created_residents.append(existing_resident)
                continue
            
            resident = Resident(**resident_data)
            db.add(resident)
            created_residents.append(resident)
            print(f"✅ Created resident: {resident.name} in {created_hoas[hoa_index].name}")
        
        # Create sample violations
        violation_types = [
            "Parking Violation",
            "Noise Complaint", 
            "Property Maintenance",
            "Pet Policy Violation",
            "Trash/Recycling",
            "Landscaping Issue",
            "Vehicle Storage",
            "Exterior Modification"
        ]
        
        violation_descriptions = [
            "Vehicle parked in unauthorized area",
            "Excessive noise after quiet hours",
            "Unmaintained property appearance",
            "Pet not on leash in common areas",
            "Trash bins left out past collection time",
            "Overgrown landscaping affecting curb appeal",
            "Recreational vehicle stored in driveway",
            "Unauthorized exterior modifications"
        ]
        
        # Create violations for each HOA
        for hoa in created_hoas:
            # Get residents for this HOA
            hoa_residents = [r for r in created_residents if r.hoa_id == hoa.id]
            
            # Create 5-8 violations per HOA
            num_violations = random.randint(5, 8)
            for i in range(num_violations):
                resident = random.choice(hoa_residents)
                violation_type = random.choice(violation_types)
                description = random.choice(violation_descriptions)
                
                # Create violation with random dates in the last 30 days
                days_ago = random.randint(0, 30)
                timestamp = datetime.utcnow() - timedelta(days=days_ago)
                
                violation = Violation(
                    violation_number=random.randint(1000, 9999),
                    description=f"{description} at {resident.address}. {violation_type}.",
                    summary=f"Summary: {violation_type} reported for {resident.name}",
                    tags=f"{violation_type}, {hoa.name}",
                    timestamp=timestamp,
                    hoa_name=hoa.name,
                    address=resident.address,
                    location="Property",
                    offender=resident.name,
                    status=random.choice(["open", "under_review", "resolved"]),
                    repeat_offender_score=random.randint(1, 5),
                    user_id=admin_user.id
                )
                
                db.add(violation)
                print(f"✅ Created violation: {violation_type} for {resident.name} in {hoa.name}")
        
        # Assign admin user to all HOAs (set hoa_id to first HOA for now)
        # Note: The current model only allows one HOA assignment per user
        # In a real system, you might want a many-to-many relationship
        admin_user.hoa_id = created_hoas[0].id
        print(f"✅ Assigned admin user to HOA: {created_hoas[0].name}")
        
        db.commit()
        
        print(f"\n🎉 Test data created successfully!")
        print(f"✅ Created {len(created_hoas)} HOAs")
        print(f"✅ Created {len(created_residents)} residents")
        print(f"✅ Created sample violations")
        print(f"✅ Admin user assigned to: {created_hoas[0].name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=== Creating Test HOAs and Sample Data ===\n")
    
    success = create_test_data()
    
    if success:
        print(f"\n🎉 You can now test the system with:")
        print(f"Username: admin")
        print(f"Password: admin123")
        print(f"URL: http://localhost:8501")
        print(f"\nThe system now has 3 test HOAs with sample violations!")
    else:
        print("\n❌ Failed to create test data.")
        sys.exit(1) 