# backend/init_db.py
# Database initialization script for A.I.ncident📊 - AI Incident Management Dashboard

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Store
from utils.auth_utils import get_password_hash
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./a_incident.db")

def init_database():
    """Initialize the database with clean test data."""
    print("🗄️ Initializing A.I.ncident📊 - AI Incident Management Dashboard database...")
    
    # Create engine and tables
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(bind=engine)  # Clean slate
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create test stores
        print("🏬 Creating test stores...")
        stores = [
            Store(id=1, name="Downtown Store", location="123 Main St, Downtown"),
            Store(id=66, name="Mall Location", location="456 Shopping Ave, Mall"),
        ]
        
        for store in stores:
            db.add(store)
        db.commit()
        print(f"✅ Created {len(stores)} stores")
        
        # Create test users
        print("👥 Creating test users...")
        users = [
            {
                "username": "admin",
                "password": "admin123",
                "role": "admin",
                "store_id": None,  # Admin has no store restriction
                "email": "admin@a_incident.com"
            },
            {
                "username": "johndoe",
                "password": "test123",
                "role": "staff",
                "store_id": 1,  # Assigned to Store #001
                "email": "john@a_incident.com"
            },
            {
                "username": "manager1",
                "password": "test123",
                "role": "staff",
                "store_id": 66,  # Assigned to Store #066
                "email": "manager@a_incident.com"
            },
            {
                "username": "employee1",
                "password": "test123",
                "role": "employee",
                "store_id": 1,  # Assigned to Store #001
                "email": "employee@a_incident.com"
            },
            {
                "username": "Jaclyn1",
                "password": "test123",
                "role": "staff",
                "store_id": 66,  # Assigned to Store #066
                "email": "jaclyn@a_incident.com"
            },
        ]
        
        for user_data in users:
            user = User(
                username=user_data["username"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
                store_id=user_data["store_id"],
                email=user_data["email"]
            )
            db.add(user)
        
        db.commit()
        print(f"✅ Created {len(users)} users")
        
        # Display created data
        print("\n📊 Database Summary:")
        print("=" * 50)
        
        stores = db.query(Store).all()
        print(f"🏬 Stores ({len(stores)}):")
        for store in stores:
            print(f"  - Store #{store.id:03d}: {store.name} - {store.location}")
        
        users = db.query(User).all()
        print(f"\n👥 Users ({len(users)}):")
        for user in users:
            store_info = "All Locations" if user.store_id is None else f"Store #{user.store_id:03d}"
            print(f"  - {user.username} ({user.role}) - {store_info}")
        
        print("\n🔑 Test Login Credentials:")
        print("=" * 50)
        print("Admin:     username=admin, password=admin123")
        print("John Doe:  username=johndoe, password=test123 (Store #001)")
        print("Manager:   username=manager1, password=test123 (Store #066)")
        print("Employee:  username=employee1, password=test123 (Store #001)")
        print("Jaclyn1:   username=Jaclyn1, password=test123 (Store #066)")
        
        print("\n✅ Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
