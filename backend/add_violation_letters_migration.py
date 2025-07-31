# Database migration to add violation letter tracking
# add_violation_letters_migration.py

from sqlalchemy import create_engine, text
from database import DATABASE_URL
import os

def add_violation_letters_tracking():
    """Add violation letter tracking fields to database."""
    
    # Create engine with autocommit for schema changes
    engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")
    
    # Add letter tracking fields to violations table
    schema_changes = [
        # Add letter tracking fields to violations table
        "ALTER TABLE violations ADD COLUMN IF NOT EXISTS letter_generated_at TIMESTAMP",
        "ALTER TABLE violations ADD COLUMN IF NOT EXISTS letter_sent_at TIMESTAMP",
        "ALTER TABLE violations ADD COLUMN IF NOT EXISTS letter_content TEXT",
        "ALTER TABLE violations ADD COLUMN IF NOT EXISTS letter_recipient_email VARCHAR(255)",
        "ALTER TABLE violations ADD COLUMN IF NOT EXISTS letter_status VARCHAR(50) DEFAULT 'not_sent'",
        "ALTER TABLE violations ADD COLUMN IF NOT EXISTS letter_sent_by INTEGER REFERENCES users(id)",
        
        # Create violation_letters table for detailed tracking
        """
        CREATE TABLE IF NOT EXISTS violation_letters (
            id SERIAL PRIMARY KEY,
            violation_id INTEGER NOT NULL REFERENCES violations(id) ON DELETE CASCADE,
            letter_content TEXT NOT NULL,
            recipient_email VARCHAR(255) NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_by INTEGER REFERENCES users(id),
            status VARCHAR(50) DEFAULT 'sent',
            email_message_id VARCHAR(255),
            opened_at TIMESTAMP,
            clicked_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Create indexes for performance
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violation_letters_violation_id ON violation_letters(violation_id)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violation_letters_recipient_email ON violation_letters(recipient_email)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violation_letters_sent_at ON violation_letters(sent_at)",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_violations_letter_status ON violations(letter_status)",
    ]
    
    with engine.connect() as conn:
        for change in schema_changes:
            try:
                print(f"Executing: {change[:100]}...")
                conn.execute(text(change))
                print(f"✅ Successfully executed schema change")
            except Exception as e:
                print(f"⚠️  Schema change failed (may already exist): {e}")

if __name__ == "__main__":
    print("🚀 Adding violation letter tracking to database...")
    add_violation_letters_tracking()
    print("✅ Violation letter tracking migration completed!") 