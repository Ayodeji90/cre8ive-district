"""Pydantic schemas for project-scoped reviews."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProjectReviewCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    brand_kit_id: uuid.UUID | None = None
    site_build_id: uuid.UUID | None = None
    review_type: str = Field(default="customer", pattern=r"^(customer|designer)$")
    notes: str | None = Field(default=None, max_length=2000)


class ProjectReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: str = Field(pattern=r"^(approved|revision_requested|rejected)$")
    notes: str | None = Field(default=None, max_length=2000)
    revision_instructions: dict[str, Any] = Field(default_factory=dict)


class ProjectReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    brand_kit_id: uuid.UUID | None
    site_build_id: uuid.UUID | None
    review_type: str
    reviewer_id: uuid.UUID | None
    status: str
    notes: str | None
    revision_instructions: dict[str, Any]
    reviewed_at: datetime | None
    deliverable_version: int
    created_at: datetime
    updated_at: datetime
