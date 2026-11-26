"""add_business_id_to_projects

Add business_id FK to projects table so legacy Business records can be
linked to their canonical Project.  The column is nullable (projects can
exist without a legacy business) and unique (one project per business).

Revision ID: e4a7b3c90d12
Revises: d93f1a2b7c04
Create Date: 2026-11-18 16:09:00.000000+00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "e4a7b3c90d12"
down_revision = "d93f1a2b7c04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column(
            "business_id",
            sa.Uuid(),
            sa.ForeignKey("businesses.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_projects_business_id", "projects", ["business_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_projects_business_id", table_name="projects")
    op.drop_column("projects", "business_id")
