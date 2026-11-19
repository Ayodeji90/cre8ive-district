"""Business-keyed workspace state: single response a frontend needs to
render the signed-in workspace for a returning customer.

Anchored on ``Business.id`` as the workspace identity, as instructed
by the blueprint and the founder.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


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

    # Business identity
    business_id: uuid.UUID
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

    # Latest deliverables (null until generated)
    brand: BrandSummary | None = None
    website: WebsiteSummary | None = None

    # Active or most recent conversation (null if never chatted)
    conversation: ConversationSummary | None = None

    # Counts for UI badges
    pending_approvals: int = 0


class ChatResumeResponse(BaseModel):
    """Response from the chat resume/start endpoint.

    ``mode`` is ``"resumed"`` when an existing conversation was reactivated,
    or ``"new"`` when a fresh conversation was started.
    """

    conversation_id: uuid.UUID
    mode: str  # "resumed" | "new"
    context: dict[str, Any] = {}
    greeting_message: str | None = None
