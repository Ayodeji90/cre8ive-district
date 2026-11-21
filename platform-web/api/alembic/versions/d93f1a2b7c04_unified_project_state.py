"""unified_project_state

Create the unified project state tables: projects, brand_kits, site_builds,
approval_queue, agent_runs, and run_events.

Revision ID: d93f1a2b7c04
Revises: c21a6e8f4d90
Create Date: 2026-11-18 15:38:00.000000+00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "d93f1a2b7c04"
down_revision = "8e1c4d6a2b90"
branch_labels = None
depends_on = None

# JSONB for Postgres, plain JSON for SQLite (tests)
json_type = sa.JSON().with_variant(JSONB(), "postgresql")


def upgrade() -> None:
    # --- projects ---
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("custom_domain", sa.String(200), unique=True, nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("industry", sa.String(80), nullable=True),
        sa.Column("location", sa.String(120), nullable=True),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("contact_email", sa.String(200), nullable=True),
        sa.Column("plan", sa.String(24), nullable=False, server_default="free"),
        sa.Column("credit_balance", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("status", sa.String(24), nullable=False, server_default="onboarding"),
        sa.Column("preferences", json_type, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- brand_kits ---
    op.create_table(
        "brand_kits",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("project_id", sa.Uuid(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("brand_name", sa.String(200), nullable=True),
        sa.Column("tagline", sa.String(300), nullable=True),
        sa.Column("palette_json", json_type, nullable=False, server_default="{}"),
        sa.Column("typography_json", json_type, nullable=False, server_default="{}"),
        sa.Column("logo_svg", sa.Text(), nullable=True),
        sa.Column("logo_urls", json_type, nullable=False, server_default="[]"),
        sa.Column("strategy", json_type, nullable=False, server_default="{}"),
        sa.Column("copy", json_type, nullable=False, server_default="{}"),
        sa.Column("offer_tiers_json", json_type, nullable=False, server_default="{}"),
        sa.Column("guidelines_pdf", sa.String(500), nullable=True),
        sa.Column("kit_zip_url", sa.String(500), nullable=True),
        sa.Column("status", sa.String(24), nullable=False, server_default="generating"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- agent_runs (created before approval_queue since approval_queue references it) ---
    op.create_table(
        "agent_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("project_id", sa.Uuid(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("goal", sa.Text(), nullable=False),
        sa.Column("credits_budget", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("credits_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_iterations", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("iteration_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(24), nullable=False, server_default="running"),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # --- site_builds ---
    op.create_table(
        "site_builds",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("project_id", sa.Uuid(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("brand_kit_id", sa.Uuid(), sa.ForeignKey("brand_kits.id", ondelete="SET NULL"), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("sandbox_id", sa.String(100), nullable=True),
        sa.Column("preview_url", sa.String(500), nullable=True),
        sa.Column("published_r2_path", sa.String(500), nullable=True),
        sa.Column("pages", json_type, nullable=False, server_default="[]"),
        sa.Column("lighthouse", json_type, nullable=True),
        sa.Column("build_status", sa.String(24), nullable=False, server_default="queued"),
        sa.Column("build_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_site_builds_project_version", "site_builds", ["project_id", "version"], unique=True)
    op.create_index("ix_site_builds_status", "site_builds", ["build_status"])

    # --- approval_queue ---
    op.create_table(
        "approval_queue",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("project_id", sa.Uuid(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("action_type", sa.String(40), nullable=False),
        sa.Column("payload_json", json_type, nullable=False, server_default="{}"),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewer_note", sa.Text(), nullable=True),
        sa.Column("agent_run_id", sa.Uuid(), sa.ForeignKey("agent_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_approval_queue_project_status", "approval_queue", ["project_id", "status"])

    # --- run_events ---
    op.create_table(
        "run_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("agent_run_id", sa.Uuid(), sa.ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("event_name", sa.String(80), nullable=True),
        sa.Column("payload", json_type, nullable=False, server_default="{}"),
        sa.Column("credits_delta", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_run_events_run_seq", "run_events", ["agent_run_id", "seq"], unique=True)


def downgrade() -> None:
    op.drop_table("run_events")
    op.drop_table("approval_queue")
    op.drop_table("site_builds")
    op.drop_table("agent_runs")
    op.drop_table("brand_kits")
    op.drop_table("projects")
