"""Add missing workspace columns

Revision ID: 002_add_missing_workspace_columns
Revises: add_resolution_fields_migration
Create Date: 2025-08-10 01:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_workspace_cols'
down_revision: Union[str, None] = '7ee7657219d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing workspace columns."""
    # Add workspace_number column to workspaces table
    op.add_column('workspaces', sa.Column('workspace_number', sa.String(), nullable=True))
    
    # Create index on workspace_number
    op.create_index(op.f('ix_workspaces_workspace_number'), 'workspaces', ['workspace_number'], unique=True)
    
    # Generate workspace numbers for existing workspaces
    # This will be handled by the application logic when workspaces are accessed


def downgrade() -> None:
    """Remove added workspace columns."""
    # Drop index
    op.drop_index(op.f('ix_workspaces_workspace_number'), table_name='workspaces')
    
    # Drop column
    op.drop_column('workspaces', 'workspace_number')
