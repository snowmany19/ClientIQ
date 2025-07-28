#!/usr/bin/env python3
"""
Script to update repeat offender scores for existing violations
based on address and resident matching.
"""

import os
import sys
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import Violation, Base
from database import get_db

def update_repeat_offender_scores():
    """Update repeat offender scores for all existing violations."""
    print("🔄 Updating repeat offender scores for existing violations...")
    
    # Create database session
    engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///./a_incident.db"))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get all violations ordered by timestamp
        violations = db.query(Violation).order_by(Violation.timestamp).all()
        print(f"📊 Found {len(violations)} violations to update")
        
        if len(violations) == 0:
            print("ℹ️ No violations found in database.")
            return
        
        # Track violations by address and offender
        address_violations = {}
        offender_violations = {}
        
        # First pass: count violations by address and offender
        for violation in violations:
            address = violation.address or ""
            offender = violation.offender or ""
            
            if address:
                if address not in address_violations:
                    address_violations[address] = []
                address_violations[address].append(violation.id)
            
            if offender:
                if offender not in offender_violations:
                    offender_violations[offender] = []
                offender_violations[offender].append(violation.id)
        
        # Second pass: update repeat offender scores
        updated_count = 0
        for violation in violations:
            address = violation.address or ""
            offender = violation.offender or ""
            
            # Count existing violations for this address or offender
            address_count = len([v for v in address_violations.get(address, []) if v < violation.id])
            offender_count = len([v for v in offender_violations.get(offender, []) if v < violation.id])
            
            # Use the higher count
            existing_violations = max(address_count, offender_count)
            
            # Calculate new score
            if existing_violations == 0:
                new_score = 1  # First-time violation
            elif existing_violations == 1:
                new_score = 2  # Second violation
            elif existing_violations == 2:
                new_score = 3  # Third violation - pattern developing
            elif existing_violations == 3:
                new_score = 4  # Fourth violation - established pattern
            else:
                new_score = 5  # Fifth+ violation - chronic offender
            
            # Update if score changed
            if violation.repeat_offender_score != new_score:
                violation.repeat_offender_score = new_score
                updated_count += 1
                print(f"  Updated Violation #{violation.id}: {violation.address} - {violation.offender} - Score: {violation.repeat_offender_score} → {new_score}")
        
        # Commit changes
        db.commit()
        print(f"✅ Updated {updated_count} violations with new repeat offender scores")
        
        # Show summary
        score_counts = db.query(
            Violation.repeat_offender_score,
            func.count(Violation.id)
        ).group_by(Violation.repeat_offender_score).all()
        
        print("\n📈 Repeat Offender Score Distribution:")
        for score, count in score_counts:
            print(f"  Score {score}: {count} violations")
        
    except Exception as e:
        print(f"❌ Error updating repeat offender scores: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_repeat_offender_scores() 