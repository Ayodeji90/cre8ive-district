"""add optional business description to waitlist signups

Revision ID: c21a6e8f4d90
Revises: b17c4d2e8a61
Create Date: 2026-11-16 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c21a6e8f4d90"
down_revision: str | None = "b17c4d2e8a61"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("waitlist_signups", sa.Column("business_description", sa.String(length=1000), nullable=True))


def downgrade() -> None:
    op.drop_column("waitlist_signups", "business_description")
