"""Fix JSON field defaults

Revision ID: 003
Revises: 002_workspace_cols
Create Date: 2025-08-17 20:17:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002_workspace_cols'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Fix JSON field defaults by updating existing NULL values to empty arrays
    op.execute("UPDATE contract_records SET risk_items = '[]'::json WHERE risk_items IS NULL")
    op.execute("UPDATE contract_records SET rewrite_suggestions = '[]'::json WHERE rewrite_suggestions IS NULL")
    op.execute("UPDATE email_templates SET variables = '[]'::json WHERE variables IS NULL")


def downgrade() -> None:
    # No downgrade needed - this is a data fix
    pass
