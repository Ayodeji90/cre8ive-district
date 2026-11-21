"""Add durable website job recovery and diagnostics."""

from alembic import op
import sqlalchemy as sa


revision: str = "a09c68f54b21"
down_revision: str | None = "3f8c1d27a9b4"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("websites", sa.Column("job_token", sa.String(length=36), nullable=True))
    op.add_column(
        "websites",
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "websites", sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column("websites", sa.Column("last_error", sa.Text(), nullable=True))
    op.create_index("ix_websites_job_token", "websites", ["job_token"], unique=False)
    op.create_index(
        "ix_websites_status_updated_at", "websites", ["status", "updated_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_websites_status_updated_at", table_name="websites")
    op.drop_index("ix_websites_job_token", table_name="websites")
    op.drop_column("websites", "last_error")
    op.drop_column("websites", "last_attempt_at")
    op.drop_column("websites", "attempt_count")
    op.drop_column("websites", "job_token")
