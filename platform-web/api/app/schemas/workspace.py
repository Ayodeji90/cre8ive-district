"""Business-keyed workspace state: single response a frontend needs to
render the signed-in workspace for a returning customer.

Anchored on ``Business.id`` as the workspace identity, as instructed
by the blueprint and the founder.
"""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.project import (
    AgentRunResponse,
    ApprovalItemResponse,
    BrandKitResponse,
    SiteBuildResponse,
)


class BusinessSummary(BaseModel):
    """Canonical business profile and billing projection."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    industry: str | None
    location: str | None
    contact_phone: str | None
    contact_email: str | None
    plan: str
    credit_balance: int
    status: str
    preferences: dict[str, Any]


class BrandSummary(BaseModel):
    """Lightweight summary of the latest brand for the workspace state."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version: int
    status: str
    strategy: dict[str, Any]
    colors: dict[str, Any]
    fonts: dict[str, Any]
    logo_urls: list  # intentionally loose: provider payloads vary
    created_at: datetime


class WebsiteSummary(BaseModel):
    """Lightweight summary of the latest website for the workspace state."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    deployment_url: str | None
    pages: list[dict[str, Any]]
    created_at: datetime


class ConversationSummary(BaseModel):
    """Enough to reconnect to an existing chat."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    context: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class WorkspaceStateResponse(BaseModel):
    """Everything a frontend needs to render the workspace for one business.

    Keyed on ``Business.id``.  Includes the latest brand, website, active
    conversation (if any), and credit balance.
    """

    business: BusinessSummary

    # Canonical Project state linked by Business.id. Project's duplicated
    # billing/profile fields remain compatibility snapshots only.
    project_id: uuid.UUID | None = None
    latest_brand_kit: BrandKitResponse | None = None
    latest_site_build: SiteBuildResponse | None = None
    active_runs: list[AgentRunResponse] = Field(default_factory=list)

    # Latest deliverables (null until generated)
    brand: BrandSummary | None = None
    website: WebsiteSummary | None = None

    # Active or most recent conversation (null if never chatted)
    active_conversation: ConversationSummary | None = None

    # Pending items are the primary projection; count is explicit for badges.
    pending_approvals: list[ApprovalItemResponse] = Field(default_factory=list)
    pending_approval_count: int = 0
    recent_approvals: list[ApprovalItemResponse] = Field(default_factory=list)


class ChatResumeResponse(BaseModel):
    """Response from the chat resume/start endpoint.

    ``mode`` is ``"resumed"`` when an existing conversation was reactivated,
    or ``"new"`` when a fresh conversation was started.
    """

    conversation_id: uuid.UUID
    mode: Literal["resumed", "new"]
    business_id: uuid.UUID
    context: dict[str, Any] = Field(default_factory=dict)
    greeting: str | None = None
