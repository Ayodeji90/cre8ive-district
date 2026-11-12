"""waitlist signups

Revision ID: 3f8c1d27a9b4
Revises: 7d2c9a41f0b6
Create Date: 2026-11-11 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "3f8c1d27a9b4"
down_revision: str | None = "7d2c9a41f0b6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "waitlist_signups",
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_waitlist_signups")),
        sa.UniqueConstraint("email", name=op.f("uq_waitlist_signups_email")),
    )


def downgrade() -> None:
    op.drop_table("waitlist_signups")
