"""auth adapter tables

Revision ID: 7d2c9a41f0b6
Revises: 46f5b7a93e33
Create Date: 2026-11-10 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "7d2c9a41f0b6"
down_revision: str | None = "46f5b7a93e33"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("provider_account_id", sa.String(length=255), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("access_token", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.Integer(), nullable=True),
        sa.Column("token_type", sa.String(length=64), nullable=True),
        sa.Column("scope", sa.Text(), nullable=True),
        sa.Column("id_token", sa.Text(), nullable=True),
        sa.Column("session_state", sa.String(length=255), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_accounts_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_accounts")),
        sa.UniqueConstraint(
            "provider", "provider_account_id", name="uq_accounts_provider_account"
        ),
    )
    op.create_index(
        op.f("ix_accounts_user_id"), "accounts", ["user_id"], unique=False
    )

    op.create_table(
        "verification_tokens",
        sa.Column("identifier", sa.String(length=320), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("expires", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint(
            "identifier", "token", name=op.f("pk_verification_tokens")
        ),
    )


def downgrade() -> None:
    op.drop_table("verification_tokens")
    op.drop_index(op.f("ix_accounts_user_id"), table_name="accounts")
    op.drop_table("accounts")
