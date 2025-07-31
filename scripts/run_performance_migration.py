#!/usr/bin/env python3
"""
Performance Migration Script
Run this script to add critical database indexes for performance optimization.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

def run_performance_migration():
    """Run the performance database migration."""
    try:
        print("🚀 Starting performance database migration...")
        
        # Import and run the migration
        from add_performance_indexes_migration import add_performance_indexes
        add_performance_indexes()
        
        print("✅ Performance migration completed successfully!")
        print("📊 Database indexes have been added for optimal performance.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_performance_migration() 