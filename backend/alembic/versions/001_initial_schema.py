"""Initial schema - create all base tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-08-10 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create workspaces table
    op.create_table('workspaces',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('company_name', sa.String(), nullable=True),
        sa.Column('contact_email', sa.String(), nullable=True),
        sa.Column('contact_phone', sa.String(), nullable=True),
        sa.Column('logo_url', sa.String(), nullable=True),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('workspace_id', sa.Integer(), nullable=True),
        sa.Column('stripe_customer_id', sa.String(), nullable=True),
        sa.Column('subscription_id', sa.String(), nullable=True),
        sa.Column('plan_id', sa.String(), nullable=True),
        sa.Column('subscription_status', sa.String(), nullable=True),
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.Column('billing_cycle_start', sa.DateTime(), nullable=True),
        sa.Column('billing_cycle_end', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create hoas table
    op.create_table('hoas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('contact_email', sa.String(), nullable=True),
        sa.Column('contact_phone', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create residents table
    op.create_table('residents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('hoa_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hoa_id'], ['hoas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create violations table
    op.create_table('violations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('violation_number', sa.String(), nullable=True),
        sa.Column('resident_id', sa.Integer(), nullable=True),
        sa.Column('hoa_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hoa_id'], ['hoas.id'], ),
        sa.ForeignKeyConstraint(['resident_id'], ['residents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_workspaces_id'), 'workspaces', ['id'], unique=False)
    op.create_index(op.f('ix_workspaces_name'), 'workspaces', ['name'], unique=False)
    op.create_index(op.f('ix_workspaces_company_name'), 'workspaces', ['company_name'], unique=False)
    
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    op.create_index(op.f('ix_hoas_id'), 'hoas', ['id'], unique=False)
    op.create_index(op.f('ix_hoas_name'), 'hoas', ['name'], unique=False)
    
    op.create_index(op.f('ix_residents_id'), 'residents', ['id'], unique=False)
    op.create_index(op.f('ix_residents_name'), 'residents', ['name'], unique=False)
    op.create_index(op.f('ix_residents_address'), 'residents', ['address'], unique=False)
    
    op.create_index(op.f('ix_violations_id'), 'violations', ['id'], unique=False)
    op.create_index(op.f('ix_violations_violation_number'), 'violations', ['violation_number'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_violations_violation_number'), table_name='violations')
    op.drop_index(op.f('ix_violations_id'), table_name='violations')
    op.drop_table('violations')
    
    op.drop_index(op.f('ix_residents_address'), table_name='residents')
    op.drop_index(op.f('ix_residents_name'), table_name='residents')
    op.drop_index(op.f('ix_residents_id'), table_name='residents')
    op.drop_table('residents')
    
    op.drop_index(op.f('ix_hoas_name'), table_name='hoas')
    op.drop_index(op.f('ix_hoas_id'), table_name='hoas')
    op.drop_table('hoas')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    op.drop_index(op.f('ix_workspaces_company_name'), table_name='workspaces')
    op.drop_index(op.f('ix_workspaces_name'), table_name='workspaces')
    op.drop_index(op.f('ix_workspaces_id'), table_name='workspaces')
    op.drop_table('workspaces')
