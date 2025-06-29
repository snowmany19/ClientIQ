# backend/assign_incidents_to_store.py
# Script to assign all existing incidents to store ID 001

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Incident, Store
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./incidentiq.db")

def assign_incidents_to_store():
    """Assign all existing incidents to store ID 001."""
    print("🔄 Assigning all incidents to Store #001...")
    
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get store ID 001
        store = db.query(Store).filter(Store.id == 1).first()
        if store is None:
            print("❌ Store ID 001 not found. Creating it...")
            store = Store(id=1, name="Downtown Store", location="123 Main St, Downtown")
            db.add(store)
            db.commit()
            print("✅ Created Store #001")
        
        # Get all incidents
        incidents = db.query(Incident).all()
        print(f"📊 Found {len(incidents)} incidents to update")
        
        if len(incidents) == 0:
            print("ℹ️ No incidents found in database.")
            return
        
        # Print all incidents before update
        print("\n📝 Incidents BEFORE update:")
        for i, incident in enumerate(incidents[:10]):
            print(f"  {i+1}. Incident #{incident.id}: store_name='{incident.store_name}' | desc='{incident.description[:40]}...'")
        if len(incidents) > 10:
            print(f"  ... and {len(incidents) - 10} more incidents")
        
        # Update all incidents to use store ID 001
        updated_count = 0
        for incident in incidents:
            if incident.store_name != store.name:
                incident.store_name = store.name
                updated_count += 1
        db.commit()
        print(f"\n✅ Successfully updated {updated_count} incidents to Store #001")
        
        # Print all incidents after update
        print("\n📝 Incidents AFTER update:")
        for i, incident in enumerate(incidents[:10]):
            print(f"  {i+1}. Incident #{incident.id}: store_name='{incident.store_name}' | desc='{incident.description[:40]}...'")
        if len(incidents) > 10:
            print(f"  ... and {len(incidents) - 10} more incidents")
        
        print("\n✅ Incident assignment complete!")
        
    except Exception as e:
        print(f"❌ Error assigning incidents: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    assign_incidents_to_store() 