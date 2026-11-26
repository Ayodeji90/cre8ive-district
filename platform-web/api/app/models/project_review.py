"""Project-scoped reviews for brand kits and site builds.

The legacy ``Review`` model (reviews.py) is scoped to Brand/Website/Order.
This model provides the blueprint's "persisted states, clear customer approvals,
optional human review, and audit trail of changes" scoped to the unified
Project → BrandKit / SiteBuild lifecycle.
"""

from __future__ import annotations

import uuid as _uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.mixins import JSONType, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class ProjectReview(UUIDMixin, TimestampMixin, Base):
    """A review request against a specific brand-kit version or site-build version.

    Lifecycle: ``pending`` → ``in_review`` → ``approved`` | ``revision_requested`` | ``rejected``
    When ``revision_requested``, a new version of the deliverable is generated
    and a fresh ProjectReview is created for it.
    """

    __tablename__ = "project_reviews"

    project_id: Mapped[_uuid.UUID] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Exactly one of these should be set
    brand_kit_id: Mapped[_uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("brand_kits.id", ondelete="CASCADE"), index=True
    )
    site_build_id: Mapped[_uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("site_builds.id", ondelete="CASCADE"), index=True
    )

    # Who is reviewing: customer or designer?
    review_type: Mapped[str] = mapped_column(
        String(16), default="customer", nullable=False
    )  # customer | designer

    # Who actually performed the review (null until claimed/decided)
    reviewer_id: Mapped[_uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL")
    )

    # pending → in_review → approved | revision_requested | rejected
    status: Mapped[str] = mapped_column(String(24), default="pending", nullable=False)

    # Free-text feedback from the reviewer
    notes: Mapped[str | None] = mapped_column(Text)

    # Structured revision instructions (what to change)
    revision_instructions: Mapped[dict[str, Any]] = mapped_column(
        JSONType, default=dict, nullable=False
    )

    # When the review was completed
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Version number of the deliverable at review time (for audit trail)
    deliverable_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    project: Mapped[Project] = relationship()
    reviewer: Mapped[User | None] = relationship()


__all__ = ["ProjectReview"]
