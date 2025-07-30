#!/usr/bin/env python3
"""
Migration script to add user profile fields (first_name, last_name, company_name, phone)
to the users table.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./a_incident.db")

def run_migration():
    """Add new user profile fields to the users table."""
    
    # Get database URL
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Check if columns already exist
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('first_name', 'last_name', 'company_name', 'phone')
            """))
            
            existing_columns = [row[0] for row in result]
            
            # Add columns that don't exist
            if 'first_name' not in existing_columns:
                print("Adding first_name column...")
                connection.execute(text("ALTER TABLE users ADD COLUMN first_name VARCHAR"))
                connection.commit()
                print("✅ Added first_name column")
            
            if 'last_name' not in existing_columns:
                print("Adding last_name column...")
                connection.execute(text("ALTER TABLE users ADD COLUMN last_name VARCHAR"))
                connection.commit()
                print("✅ Added last_name column")
            
            if 'company_name' not in existing_columns:
                print("Adding company_name column...")
                connection.execute(text("ALTER TABLE users ADD COLUMN company_name VARCHAR"))
                connection.commit()
                print("✅ Added company_name column")
            
            if 'phone' not in existing_columns:
                print("Adding phone column...")
                connection.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR"))
                connection.commit()
                print("✅ Added phone column")
            
            print("\n🎉 Migration completed successfully!")
            print("All user profile fields have been added to the users table.")
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔄 Starting user profile fields migration...")
    run_migration() 