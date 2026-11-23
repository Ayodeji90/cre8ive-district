"""Unified project state: replaces the fragmented business/brand/website/agent-run
models with a single canonical project record and its child tables.

The ``Business`` model is renamed to ``Project`` (keeping the same ``businesses``
table for backward compatibility with existing data, then aliased through a migration).
New child tables:

- brand_kits       — structured brand deliverables (palette, typography, logo SVG, etc.)
- site_builds      — versioned website builds with preview/publish lifecycle
- approval_queue   — "Needs Your OK" gate for destructive or public actions
- agent_runs       — persistent audit log of every Abija tool call
- run_events       — individual events within a run
"""

from __future__ import annotations

import uuid as _uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.mixins import JSONType, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.user import User


# ---------------------------------------------------------------------------
# Project (the canonical workspace record — evolves from Business)
# ---------------------------------------------------------------------------


class Project(UUIDMixin, TimestampMixin, Base):
    """A customer workspace that owns every deliverable: brand kits, site builds,
    conversations, orders, credits, and agent runs.

    Linked to a legacy ``Business`` record via ``business_id`` so that the
    existing intake/chat flow (which writes to Business) stays intact while new
    workflows route through Project.
    """

    __tablename__ = "projects"

    user_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Optional link to the legacy Business record this project was created from.
    business_id: Mapped[_uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("businesses.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        index=True,
    )
    # Public slug for *.cre8ivedistrict.app subdomain
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    custom_domain: Mapped[str | None] = mapped_column(String(200), unique=True)

    # Basic info (carried over from Business)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    industry: Mapped[str | None] = mapped_column(String(80))
    location: Mapped[str | None] = mapped_column(String(120))
    contact_phone: Mapped[str | None] = mapped_column(String(20))
    contact_email: Mapped[str | None] = mapped_column(String(200))

    # Billing
    plan: Mapped[str] = mapped_column(String(24), default="free", nullable=False)
    credit_balance: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    # Lifecycle: onboarding → briefing → generating → review → active → paused
    status: Mapped[str] = mapped_column(String(24), default="onboarding", nullable=False)

    # Flexible metadata (target_audience, mood, style_keywords, services, etc.)
    preferences: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)

    # Relationships
    owner: Mapped[User] = relationship(foreign_keys=[user_id])
    business: Mapped[Business | None] = relationship(foreign_keys=[business_id])
    brand_kits: Mapped[list[BrandKit]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="BrandKit.version.desc()",
    )
    site_builds: Mapped[list[SiteBuild]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="SiteBuild.version.desc()",
    )
    approval_queue: Mapped[list[ApprovalItem]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ApprovalItem.created_at.desc()",
    )
    agent_runs: Mapped[list[AgentRun]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="AgentRun.created_at.desc()",
    )


# ---------------------------------------------------------------------------
# BrandKit — structured brand deliverables
# ---------------------------------------------------------------------------


class BrandKit(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "brand_kits"
    __table_args__ = (
        CheckConstraint("version > 0", name="ck_brand_kits_version_positive"),
        CheckConstraint(
            "status IN ('generating', 'ready_for_review', 'approved', 'revision_requested', 'superseded', 'failed')",
            name="ck_brand_kits_status",
        ),
    )

    project_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Core brand identity
    brand_name: Mapped[str | None] = mapped_column(String(200))
    tagline: Mapped[str | None] = mapped_column(String(300))
    palette_json: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    typography_json: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    logo_svg: Mapped[str | None] = mapped_column(Text)  # raw SVG markup
    logo_urls: Mapped[list[dict[str, Any]]] = mapped_column(JSONType, default=list, nullable=False)

    # Strategy & copy
    strategy: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    copy: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)

    # Offer structure for the customer's business
    offer_tiers_json: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)

    # Deliverable files
    guidelines_pdf: Mapped[str | None] = mapped_column(String(500))
    kit_zip_url: Mapped[str | None] = mapped_column(String(500))

    # generating → ready_for_review → approved → superseded
    status: Mapped[str] = mapped_column(String(24), default="generating", nullable=False)

    project: Mapped[Project] = relationship(back_populates="brand_kits")


# ---------------------------------------------------------------------------
# SiteBuild — versioned website builds with preview/publish lifecycle
# ---------------------------------------------------------------------------


class SiteBuild(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "site_builds"
    __table_args__ = (
        Index("ix_site_builds_project_version", "project_id", "version", unique=True),
        Index("ix_site_builds_status", "build_status"),
        CheckConstraint("version > 0", name="ck_site_builds_version_positive"),
        CheckConstraint(
            "build_status IN ('queued', 'building', 'preview_ready', 'publishing', 'published', 'failed')",
            name="ck_site_builds_status",
        ),
    )

    project_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    brand_kit_id: Mapped[_uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("brand_kits.id", ondelete="SET NULL")
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Cloudflare R2 / preview hosting
    sandbox_id: Mapped[str | None] = mapped_column(String(100))
    preview_url: Mapped[str | None] = mapped_column(String(500))
    published_r2_path: Mapped[str | None] = mapped_column(String(500))

    # Build output
    pages: Mapped[list[dict[str, Any]]] = mapped_column(JSONType, default=list, nullable=False)
    lighthouse: Mapped[dict[str, Any] | None] = mapped_column(JSONType)

    # queued → building → preview_ready → publishing → published → failed
    build_status: Mapped[str] = mapped_column(String(24), default="queued", nullable=False)
    build_error: Mapped[str | None] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="site_builds")


# ---------------------------------------------------------------------------
# ApprovalQueue — the "Needs Your OK" gate
# ---------------------------------------------------------------------------


class ApprovalItem(UUIDMixin, TimestampMixin, Base):
    """Every destructive or public action Abija wants to take goes through here.
    The user must approve or reject before execution."""

    __tablename__ = "approval_queue"
    __table_args__ = (
        Index("ix_approval_queue_project_status", "project_id", "status"),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'expired')",
            name="ck_approval_queue_status",
        ),
        CheckConstraint(
            "decision IS NULL OR decision IN ('approved', 'rejected', 'expired')",
            name="ck_approval_queue_decision",
        ),
        CheckConstraint(
            "execution_status IN ('not_started', 'queued', 'running', 'succeeded', 'failed')",
            name="ck_approval_queue_execution_status",
        ),
        CheckConstraint(
            "execution_status != 'succeeded' OR (executed_at IS NOT NULL AND idempotency_key IS NOT NULL AND execution_outcome IS NOT NULL)",
            name="ck_approval_queue_execution_completion",
        ),
    )

    project_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # What kind of action: send_email, publish_social, deploy_site, purchase_domain, etc.
    action_type: Mapped[str] = mapped_column(String(40), nullable=False)
    # Full payload describing what will happen on approval
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    # pending → approved → rejected → expired
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    # Decision and execution are separate durable lifecycle stages. ``status``
    # remains as a legacy field; ``decision`` is canonical going forward.
    decision: Mapped[str | None] = mapped_column(String(16))
    reviewer_id: Mapped[_uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL")
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    execution_status: Mapped[str] = mapped_column(String(20), default="not_started", nullable=False)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    execution_outcome: Mapped[dict[str, Any] | None] = mapped_column(JSONType)
    idempotency_key: Mapped[str | None] = mapped_column(String(200), unique=True)
    # Optional reviewer note
    reviewer_note: Mapped[str | None] = mapped_column(Text)
    # Which agent run created this approval request?
    agent_run_id: Mapped[_uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("agent_runs.id", ondelete="SET NULL")
    )

    project: Mapped[Project] = relationship(back_populates="approval_queue")
    agent_run: Mapped[AgentRun | None] = relationship()

    @property
    def summary(self) -> str:
        """Short human-readable action summary for workspace projections."""
        value = self.payload_json.get("summary") if self.payload_json else None
        return str(value or self.action_type.replace("_", " ").capitalize())


# ---------------------------------------------------------------------------
# AgentRun & RunEvent — persistent audit log of every tool call
# ---------------------------------------------------------------------------


class AgentRun(UUIDMixin, TimestampMixin, Base):
    """A single invocation of Abija's autonomous loop for a project."""

    __tablename__ = "agent_runs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('running', 'paused_needs_approval', 'completed', 'failed', 'cancelled')",
            name="ck_agent_runs_status",
        ),
        CheckConstraint(
            "credits_budget >= 0 AND credits_used >= 0 AND max_iterations > 0 AND iteration_count >= 0",
            name="ck_agent_runs_counters",
        ),
    )

    project_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # What the user asked Abija to do
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    # How many credits were reserved for this run
    credits_budget: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    credits_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # How many iterations were allowed / used
    max_iterations: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    iteration_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # running → paused_needs_approval → completed → failed → cancelled
    status: Mapped[str] = mapped_column(String(24), default="running", nullable=False)
    # Final summary / error
    result_summary: Mapped[str | None] = mapped_column(Text)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    project: Mapped[Project] = relationship(back_populates="agent_runs")
    events: Mapped[list[RunEvent]] = relationship(
        back_populates="agent_run",
        cascade="all, delete-orphan",
        order_by="RunEvent.seq",
    )


class RunEvent(UUIDMixin, Base):
    """Individual event within an agent run: tool calls, approvals, results."""

    __tablename__ = "run_events"
    __table_args__ = (Index("ix_run_events_run_seq", "agent_run_id", "seq", unique=True),)

    agent_run_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid, ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    # tool_call, tool_result, approval_requested, approval_resolved, thought, error
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    # tool name, approval action type, etc.
    event_name: Mapped[str | None] = mapped_column(String(80))
    # Full event payload
    payload: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    # Credits consumed by this specific event
    credits_delta: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    agent_run: Mapped[AgentRun] = relationship(back_populates="events")


__all__ = [
    "Project",
    "BrandKit",
    "SiteBuild",
    "ApprovalItem",
    "AgentRun",
    "RunEvent",
]
