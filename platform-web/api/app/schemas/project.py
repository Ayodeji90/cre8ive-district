"""Pydantic schemas for the unified project state."""

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------


class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)
    slug: str | None = Field(
        default=None, max_length=100, pattern=r"^[a-z0-9][a-z0-9-]{1,98}[a-z0-9]$"
    )
    description: str | None = None
    industry: str | None = Field(default=None, max_length=80)
    location: str | None = Field(default=None, max_length=120)
    contact_phone: str | None = Field(default=None, max_length=20)
    contact_email: str | None = Field(default=None, max_length=200)
    preferences: dict[str, Any] = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    industry: str | None = Field(default=None, max_length=80)
    location: str | None = Field(default=None, max_length=120)
    contact_phone: str | None = Field(default=None, max_length=20)
    contact_email: str | None = Field(default=None, max_length=200)
    custom_domain: str | None = Field(default=None, max_length=200)
    preferences: dict[str, Any] | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    business_id: uuid.UUID | None
    name: str
    slug: str
    custom_domain: str | None
    description: str | None
    industry: str | None
    location: str | None
    contact_phone: str | None
    contact_email: str | None
    # Deprecated compatibility snapshots. Business is authoritative for these.
    plan: str
    credit_balance: int
    status: str
    preferences: dict[str, Any]
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# BrandKit
# ---------------------------------------------------------------------------


class BrandKitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    version: int
    brand_name: str | None
    tagline: str | None
    palette_json: dict[str, Any]
    typography_json: dict[str, Any]
    logo_svg: str | None
    logo_urls: list[dict[str, Any]]
    strategy: dict[str, Any]
    copy: dict[str, Any]
    offer_tiers_json: dict[str, Any]
    guidelines_pdf: str | None
    kit_zip_url: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class BrandKitUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    brand_name: str | None = None
    tagline: str | None = None
    palette_json: dict[str, Any] | None = None
    typography_json: dict[str, Any] | None = None
    logo_svg: str | None = None
    offer_tiers_json: dict[str, Any] | None = None
    status: Literal["generating", "ready_for_review", "approved", "superseded", "failed"] | None = (
        None
    )


# ---------------------------------------------------------------------------
# SiteBuild
# ---------------------------------------------------------------------------


class SiteBuildResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    brand_kit_id: uuid.UUID | None
    version: int
    sandbox_id: str | None
    preview_url: str | None
    published_r2_path: str | None
    pages: list[dict[str, Any]]
    lighthouse: dict[str, Any] | None
    build_status: str
    build_error: str | None
    created_at: datetime
    updated_at: datetime


class SiteBuildCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    brand_kit_id: uuid.UUID | None = None


# ---------------------------------------------------------------------------
# ApprovalQueue
# ---------------------------------------------------------------------------


class ApprovalItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_run_id: uuid.UUID | None
    action_type: str
    summary: str
    decision: Optional[Literal["approved", "rejected", "expired"]] = None  # noqa: UP045
    decided_at: datetime | None
    execution_status: Literal["not_started", "queued", "running", "succeeded", "failed"]
    executed_at: datetime | None
    execution_outcome: dict[str, Any] | None


class ApprovalDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: str = Field(pattern=r"^(approved|rejected)$")
    reviewer_note: str | None = Field(default=None, max_length=1000)


# ---------------------------------------------------------------------------
# AgentRun
# ---------------------------------------------------------------------------


class AgentRunCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: uuid.UUID
    goal: str = Field(min_length=8, max_length=1000)
    credits_budget: int | None = Field(default=None, ge=1, le=10000)
    max_iterations: int = Field(default=20, ge=1, le=100)


class AgentRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    goal: str
    credits_budget: int
    credits_used: int
    max_iterations: int
    iteration_count: int
    status: str
    result_summary: str | None
    finished_at: datetime | None
    created_at: datetime
    updated_at: datetime


class RunEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_run_id: uuid.UUID
    seq: int
    event_type: str
    event_name: str | None
    payload: dict[str, Any]
    credits_delta: int
    created_at: datetime
