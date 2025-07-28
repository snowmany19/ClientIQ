"""add resolution tracking fields

Revision ID: add_resolution_fields_001
Revises: bde1bc73822b
Create Date: 2025-07-11 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_resolution_fields_002'
down_revision: Union[str, None] = '5101db895863'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add resolution tracking fields to violations table."""
    # Add new columns for resolution tracking
    op.add_column('violations', sa.Column('resolved_at', sa.DateTime(), nullable=True))
    op.add_column('violations', sa.Column('resolved_by', sa.String(), nullable=True))
    op.add_column('violations', sa.Column('resolution_notes', sa.Text(), nullable=True))
    op.add_column('violations', sa.Column('reviewed_at', sa.DateTime(), nullable=True))
    op.add_column('violations', sa.Column('reviewed_by', sa.String(), nullable=True))


def downgrade() -> None:
    """Remove resolution tracking fields from violations table."""
    # Remove the columns we added
    op.drop_column('violations', 'reviewed_by')
    op.drop_column('violations', 'reviewed_at')
    op.drop_column('violations', 'resolution_notes')
    op.drop_column('violations', 'resolved_by')
    op.drop_column('violations', 'resolved_at') 