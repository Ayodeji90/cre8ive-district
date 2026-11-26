"""create_project_reviews_table

Add project_reviews table for tracking reviews and revisions on brand kits and site builds.

Revision ID: f5b8c4d1e234
Revises: e4a7b3c90d12
Create Date: 2026-11-18 16:29:00.000000+00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "f5b8c4d1e234"
down_revision = "e4a7b3c90d12"
branch_labels = None
depends_on = None

json_type = sa.JSON().with_variant(JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "project_reviews",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("project_id", sa.Uuid(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("brand_kit_id", sa.Uuid(), sa.ForeignKey("brand_kits.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("site_build_id", sa.Uuid(), sa.ForeignKey("site_builds.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("review_type", sa.String(16), nullable=False, server_default="customer"),
        sa.Column("reviewer_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("revision_instructions", json_type, nullable=False, server_default="{}"),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deliverable_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("project_reviews")
