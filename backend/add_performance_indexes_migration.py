# Database migration to add performance indexes
# add_performance_indexes_migration.py

from sqlalchemy import create_engine, text
from database import DATABASE_URL
import os

def add_performance_indexes():
    """Add critical database indexes for performance optimization."""
    
    # Create engine with autocommit for index creation
    engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")
    
    # Critical indexes for performance
    indexes = [
        # Violations table indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violations_timestamp ON violations(timestamp)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violations_hoa_id ON violations(hoa_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violations_status ON violations(status)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violations_user_id ON violations(user_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violations_offender ON violations(offender)",
        
        # Users table indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username ON users(username)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_stripe_customer_id ON users(stripe_customer_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role ON users(role)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_hoa_id ON users(hoa_id)",
        
        # HOA table indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_hoas_name ON hoas(name)",
        
        # Residents table indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_residents_hoa_id ON residents(hoa_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_residents_address ON residents(address)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_residents_email ON residents(email)",
        
        # Communications table indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_communications_violation_id ON communications(violation_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_communications_sent_at ON communications(sent_at)",
        
        # User sessions table indexes
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at)",
        
        # Composite indexes for common query patterns
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violations_hoa_status ON violations(hoa_id, status)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violations_user_timestamp ON violations(user_id, timestamp)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_residents_hoa_address ON residents(hoa_id, address)",
    ]
    
    with engine.connect() as conn:
        for index_sql in indexes:
            try:
                print(f"Creating index: {index_sql}")
                conn.execute(text(index_sql))
                print(f"✅ Successfully created index")
            except Exception as e:
                print(f"⚠️  Index creation failed (may already exist): {e}")

if __name__ == "__main__":
    print("🚀 Adding performance indexes to database...")
    add_performance_indexes()
    print("✅ Performance indexes migration completed!") 