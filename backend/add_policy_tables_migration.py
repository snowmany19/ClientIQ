#!/usr/bin/env python3
"""
Migration script to add policy_documents and policy_sections tables
for HOA policy customization feature.
"""

import sys
import os
from sqlalchemy import create_engine, text
from core.config import get_settings

def run_migration():
    """Run the migration to create policy tables."""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        try:
            # Create policy_documents table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS policy_documents (
                    id SERIAL PRIMARY KEY,
                    hoa_id INTEGER NOT NULL REFERENCES hoas(id),
                    name VARCHAR NOT NULL,
                    content TEXT,
                    version VARCHAR DEFAULT '1.0',
                    effective_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR DEFAULT 'draft',
                    uploaded_by INTEGER REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create policy_sections table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS policy_sections (
                    id SERIAL PRIMARY KEY,
                    policy_id INTEGER NOT NULL REFERENCES policy_documents(id) ON DELETE CASCADE,
                    title VARCHAR NOT NULL,
                    content TEXT,
                    category VARCHAR,
                    severity VARCHAR DEFAULT 'medium',
                    penalties JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            
            # Create indexes for better performance
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_policy_documents_hoa_id ON policy_documents(hoa_id);
                CREATE INDEX IF NOT EXISTS idx_policy_documents_status ON policy_documents(status);
                CREATE INDEX IF NOT EXISTS idx_policy_sections_policy_id ON policy_sections(policy_id);
                CREATE INDEX IF NOT EXISTS idx_policy_sections_category ON policy_sections(category);
            """))
            
            conn.commit()
            print("✅ Policy tables created successfully!")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error creating policy tables: {e}")
            sys.exit(1)

if __name__ == "__main__":
    run_migration() 