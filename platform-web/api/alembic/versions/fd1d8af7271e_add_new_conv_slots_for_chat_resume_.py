"""add_new_conv_slots_for_chat_resume_serialization

Revision ID: fd1d8af7271e
Revises: g6c9d5e2f345
Create Date: 2026-11-20 17:57:05.374105
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "fd1d8af7271e"
down_revision: str | None = "g6c9d5e2f345"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "new_conv_slots",
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["business_id"],
            ["businesses.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("business_id", "owner_id"),
    )


def downgrade() -> None:
    op.drop_table("new_conv_slots")
