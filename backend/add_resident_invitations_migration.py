"""
Migration to add resident_invitations table
"""
from sqlalchemy import create_engine, text
from core.config import get_settings

def migrate():
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Create resident_invitations table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS resident_invitations (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                hoa_id INTEGER NOT NULL REFERENCES hoas(id) ON DELETE CASCADE,
                token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                invited_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                unit_number VARCHAR(50) NOT NULL,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Add indexes for performance
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_resident_invitations_token 
            ON resident_invitations(token)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_resident_invitations_hoa_id 
            ON resident_invitations(hoa_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_resident_invitations_expires_at 
            ON resident_invitations(expires_at)
        """))
        
        conn.commit()
        print("✅ Resident invitations table created successfully")

if __name__ == "__main__":
    migrate() 