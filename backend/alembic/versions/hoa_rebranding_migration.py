"""HOA Rebranding Migration

Revision ID: hoa_rebranding_001
Revises: 506bc90b77b3
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'hoa_rebranding_001'
down_revision = '506bc90b77b3'
branch_labels = None
depends_on = None


def upgrade():
    # Create new HOA table
    op.create_table('hoas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('contact_email', sa.String(), nullable=True),
        sa.Column('contact_phone', sa.String(), nullable=True),
        sa.Column('logo_url', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create new Resident table
    op.create_table('residents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('hoa_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('violation_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['hoa_id'], ['hoas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create new Violation table
    op.create_table('violations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('violation_number', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('tags', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('hoa_name', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('offender', sa.String(), nullable=True),
        sa.Column('gps_coordinates', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('repeat_offender_score', sa.Integer(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('pdf_path', sa.String(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add new columns to users table
    op.add_column('users', sa.Column('hoa_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'hoas', ['hoa_id'], ['id'])
    
    # Migrate data from old tables to new tables
    # This is a simplified migration - in production you'd want more sophisticated data mapping
    
    # Insert default HOA if stores table exists
    connection = op.get_bind()
    if connection.dialect.has_table(connection, 'stores'):
        # Migrate stores to HOAs
        op.execute("""
            INSERT INTO hoas (id, name, location)
            SELECT id, name, location FROM stores
        """)
        
        # Update users to reference HOAs instead of stores
        op.execute("""
            UPDATE users SET hoa_id = store_id WHERE store_id IS NOT NULL
        """)
    
    # Migrate incidents to violations if incidents table exists
    if connection.dialect.has_table(connection, 'incidents'):
        op.execute("""
            INSERT INTO violations (
                id, description, summary, tags, timestamp, 
                hoa_name, location, offender, image_url, pdf_path, user_id
            )
            SELECT 
                id, description, summary, tags, timestamp,
                store_name, location, offender, image_url, pdf_path, user_id
            FROM incidents
        """)
        
        # Add violation numbers
        op.execute("""
            UPDATE violations 
            SET violation_number = id 
            WHERE violation_number IS NULL
        """)
        
        # Set default values for new columns
        op.execute("""
            UPDATE violations 
            SET 
                status = 'open',
                repeat_offender_score = 1,
                address = location
            WHERE status IS NULL
        """)
    
    # Drop old tables if they exist
    if connection.dialect.has_table(connection, 'incidents'):
        op.drop_table('incidents')

    if connection.dialect.has_table(connection, 'stores'):
        # Drop the foreign key constraint before dropping the stores table
        op.drop_constraint('users_store_id_fkey', 'users', type_='foreignkey')
        op.drop_table('stores')

    if connection.dialect.has_table(connection, 'offenders'):
        op.drop_table('offenders')

    # Remove old columns from users table
    op.drop_column('users', 'store_id')


def downgrade():
    # This is a destructive migration - recreate old tables
    # Note: This will lose data that was added after the migration
    
    # Recreate stores table
    op.create_table('stores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate incidents table
    op.create_table('incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('tags', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('store_name', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('offender', sa.String(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('pdf_path', sa.String(), nullable=True),
        sa.Column('severity', sa.String(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate offenders table
    op.create_table('offenders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('alias', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add back store_id to users
    op.add_column('users', sa.Column('store_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'users', 'stores', ['store_id'], ['id'])
    
    # Migrate data back (simplified)
    # Note: This is a destructive migration - data added after the initial migration will be lost
    
    # Drop new tables first
    op.drop_table('violations')
    op.drop_table('residents')
    op.drop_table('hoas')
    
    # Remove new columns from users
    try:
        op.drop_constraint('users_hoa_id_fkey', 'users', type_='foreignkey')
    except:
        pass  # Constraint might not exist or have different name
    op.drop_column('users', 'hoa_id') 