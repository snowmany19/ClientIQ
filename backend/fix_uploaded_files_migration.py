#!/usr/bin/env python3
"""
Migration script to fix uploaded_files field for existing contracts.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from models import ContractRecord
from sqlalchemy import text

def fix_uploaded_files():
    """Fix uploaded_files field for existing contracts."""
    db = next(get_db())
    
    try:
        # Check database type
        db_url = str(db.bind.url)
        is_sqlite = 'sqlite' in db_url.lower()
        
        if is_sqlite:
            # SQLite syntax
            result = db.execute(
                text("UPDATE contract_records SET uploaded_files = '[]' WHERE uploaded_files IS NULL")
            )
        else:
            # PostgreSQL syntax
            result = db.execute(
                text("UPDATE contract_records SET uploaded_files = '[]'::json WHERE uploaded_files IS NULL")
            )
        
        # Commit the changes
        db.commit()
        
        print(f"✅ Updated {result.rowcount} contracts with NULL uploaded_files")
        
        # Verify the fix
        contracts = db.query(ContractRecord).all()
        for contract in contracts:
            if contract.uploaded_files is None:
                print(f"⚠️  Contract {contract.id} still has NULL uploaded_files")
            else:
                print(f"✅ Contract {contract.id} has uploaded_files: {contract.uploaded_files}")
                
    except Exception as e:
        print(f"❌ Error fixing uploaded_files: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Fixing uploaded_files field for existing contracts...")
    fix_uploaded_files()
    print("✅ Migration complete!")
