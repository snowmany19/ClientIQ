#!/usr/bin/env python3
"""
Migration script to add user settings fields to the User table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from core.config import get_settings

settings = get_settings()

def run_migration():
    """Add user settings fields to User table"""
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Add new columns to users table
        migrations = [
            # Security fields
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS two_factor_secret VARCHAR;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN DEFAULT FALSE;",
            
            # User settings fields
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS notification_email BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS notification_push BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS notification_violations BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS notification_reports BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS theme_preference VARCHAR DEFAULT 'light';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS pwa_offline_enabled BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS pwa_app_switcher_enabled BOOLEAN DEFAULT TRUE;",
            
            # Timestamp fields
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMP;",
        ]
        
        for migration in migrations:
            try:
                conn.execute(text(migration))
                print(f"✅ Executed: {migration}")
            except Exception as e:
                print(f"⚠️  Skipped (column may already exist): {migration}")
                print(f"   Error: {e}")
        
        # Create user_sessions table
        create_sessions_table = """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            session_token VARCHAR UNIQUE NOT NULL,
            device_info VARCHAR,
            ip_address VARCHAR,
            location VARCHAR,
            user_agent VARCHAR,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL
        );
        """
        
        try:
            conn.execute(text(create_sessions_table))
            print("✅ Created user_sessions table")
        except Exception as e:
            print(f"⚠️  user_sessions table may already exist: {e}")
        
        conn.commit()
        print("🎉 Migration completed successfully!")

if __name__ == "__main__":
    run_migration() 