"""separate approval decisions from capability execution

Revision ID: h7d0e6f3a912
Revises: fd1d8af7271e
Create Date: 2026-11-23 00:00:00.000000+00:00
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision = "h7d0e6f3a912"
down_revision = "fd1d8af7271e"
branch_labels = None
depends_on = None
json_type = sa.JSON().with_variant(JSONB(), "postgresql")


def upgrade() -> None:
    op.add_column("approval_queue", sa.Column("decision", sa.String(16), nullable=True))
    op.add_column("approval_queue", sa.Column("reviewer_id", sa.Uuid(), nullable=True))
    op.add_column(
        "approval_queue", sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "approval_queue",
        sa.Column("execution_status", sa.String(20), server_default="not_started", nullable=False),
    )
    op.add_column(
        "approval_queue",
        sa.Column("execution_outcome", json_type, nullable=True),
    )
    op.add_column("approval_queue", sa.Column("idempotency_key", sa.String(200), nullable=True))
    op.create_foreign_key(
        "fk_approval_queue_reviewer_id_users",
        "approval_queue",
        "users",
        ["reviewer_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_unique_constraint(
        "uq_approval_queue_idempotency_key", "approval_queue", ["idempotency_key"]
    )

    # Backfill existing decision state while leaving execution explicitly pending.
    op.execute(
        "UPDATE approval_queue SET decision = status, decided_at = updated_at "
        "WHERE status IN ('approved', 'rejected')"
    )
    op.create_check_constraint(
        "ck_approval_queue_status",
        "approval_queue",
        "status IN ('pending', 'approved', 'rejected', 'expired')",
    )
    op.create_check_constraint(
        "ck_approval_queue_decision",
        "approval_queue",
        "decision IS NULL OR decision IN ('approved', 'rejected', 'expired')",
    )
    op.create_check_constraint(
        "ck_approval_queue_execution_status",
        "approval_queue",
        "execution_status IN ('not_started', 'queued', 'running', 'succeeded', 'failed')",
    )
    op.create_check_constraint(
        "ck_approval_queue_execution_completion",
        "approval_queue",
        "execution_status != 'succeeded' OR (executed_at IS NOT NULL AND idempotency_key IS NOT NULL AND execution_outcome IS NOT NULL)",
    )
    op.create_check_constraint("ck_brand_kits_version_positive", "brand_kits", "version > 0")
    op.create_check_constraint(
        "ck_brand_kits_status",
        "brand_kits",
        "status IN ('generating', 'ready_for_review', 'approved', 'revision_requested', 'superseded', 'failed')",
    )
    op.create_check_constraint("ck_site_builds_version_positive", "site_builds", "version > 0")
    op.create_check_constraint(
        "ck_site_builds_status",
        "site_builds",
        "build_status IN ('queued', 'building', 'preview_ready', 'publishing', 'published', 'failed')",
    )
    op.create_check_constraint(
        "ck_agent_runs_status",
        "agent_runs",
        "status IN ('running', 'paused_needs_approval', 'completed', 'failed', 'cancelled')",
    )
    op.create_check_constraint(
        "ck_agent_runs_counters",
        "agent_runs",
        "credits_budget >= 0 AND credits_used >= 0 AND max_iterations > 0 AND iteration_count >= 0",
    )


def downgrade() -> None:
    for name, table in (
        ("ck_agent_runs_counters", "agent_runs"),
        ("ck_agent_runs_status", "agent_runs"),
        ("ck_site_builds_status", "site_builds"),
        ("ck_site_builds_version_positive", "site_builds"),
        ("ck_brand_kits_status", "brand_kits"),
        ("ck_brand_kits_version_positive", "brand_kits"),
        ("ck_approval_queue_execution_completion", "approval_queue"),
        ("ck_approval_queue_execution_status", "approval_queue"),
        ("ck_approval_queue_decision", "approval_queue"),
        ("ck_approval_queue_status", "approval_queue"),
    ):
        op.drop_constraint(name, table, type_="check")
    op.drop_constraint("uq_approval_queue_idempotency_key", "approval_queue", type_="unique")
    op.drop_constraint("fk_approval_queue_reviewer_id_users", "approval_queue", type_="foreignkey")
    for column in (
        "idempotency_key",
        "execution_outcome",
        "execution_status",
        "decided_at",
        "reviewer_id",
        "decision",
    ):
        op.drop_column("approval_queue", column)
