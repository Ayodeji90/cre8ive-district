"""Build the Business-keyed workspace state response.

Collects latest brand, website, active conversation, and pending approval
count into a single response that the frontend fetches on workspace load.
"""

from __future__ import annotations

from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging import get_logger
from app.models.brand import Brand
from app.models.business import Business
from app.models.conversation import Conversation
from app.models.project import AgentRun, ApprovalItem, BrandKit, Project, SiteBuild
from app.models.website import Website
from app.schemas.workspace import (
    BrandSummary,
    ConversationSummary,
    WebsiteSummary,
    WorkspaceStateResponse,
)

log = get_logger(__name__)


async def build_workspace_state(
    db: AsyncSession,
    business: Business,
) -> WorkspaceStateResponse:
    """Assemble workspace state keyed on Business.id."""

    # Latest brand
    brand_row = (
        (
            await db.execute(
                select(Brand)
                .where(Brand.business_id == business.id)
                .order_by(Brand.created_at.desc())
            )
        )
        .scalars()
        .first()
    )
    brand = BrandSummary.model_validate(brand_row) if brand_row else None

    # Latest website
    website_row = (
        (
            await db.execute(
                select(Website)
                .where(Website.business_id == business.id)
                .order_by(Website.created_at.desc())
            )
        )
        .scalars()
        .first()
    )
    website = WebsiteSummary.model_validate(website_row) if website_row else None

    # Most recent conversation — explicit status priority: active > idle > closed
    status_priority = case(
        (Conversation.status == "active", 0),
        (Conversation.status == "idle", 1),
        else_=2,
    )
    convo_row = (
        (
            await db.execute(
                select(Conversation)
                .where(
                    Conversation.business_id == business.id,
                    Conversation.user_id == business.owner_id,
                )
                .order_by(
                    status_priority,
                    Conversation.updated_at.desc(),
                )
            )
        )
        .scalars()
        .first()
    )
    conversation = ConversationSummary.model_validate(convo_row) if convo_row else None

    # Pending approval count (from Project if one is linked)
    pending_approvals = []
    pending_approval_count = 0
    project_id = None
    latest_brand_kit = None
    latest_site_build = None
    active_runs = []
    recent_approvals = []
    project = await db.scalar(select(Project).where(Project.business_id == business.id))
    if project is not None:
        project_id = project.id
        latest_brand_kit = await db.scalar(
            select(BrandKit)
            .where(BrandKit.project_id == project.id)
            .order_by(BrandKit.version.desc(), BrandKit.created_at.desc())
            .limit(1)
        )
        latest_site_build = await db.scalar(
            select(SiteBuild)
            .where(SiteBuild.project_id == project.id)
            .order_by(SiteBuild.version.desc(), SiteBuild.created_at.desc())
            .limit(1)
        )
        active_runs = list(
            (
                await db.execute(
                    select(AgentRun)
                    .where(
                        AgentRun.project_id == project.id,
                        AgentRun.status.in_(("running", "paused_needs_approval")),
                    )
                    .order_by(AgentRun.created_at.desc())
                )
            )
            .scalars()
            .all()
        )
        recent_approvals = list(
            (
                await db.execute(
                    select(ApprovalItem)
                    .where(ApprovalItem.project_id == project.id)
                    .order_by(ApprovalItem.created_at.desc())
                    .limit(10)
                )
            )
            .scalars()
            .all()
        )
        pending_approvals = list(
            (
                await db.execute(
                    select(ApprovalItem)
                    .where(
                        ApprovalItem.project_id == project.id,
                        ApprovalItem.decision.is_(None),
                    )
                    .order_by(ApprovalItem.created_at.desc())
                )
            )
            .scalars()
            .all()
        )
        pending_approval_count = len(pending_approvals)

    return WorkspaceStateResponse(
        business=business,
        project_id=project_id,
        latest_brand_kit=latest_brand_kit,
        latest_site_build=latest_site_build,
        active_runs=active_runs,
        recent_approvals=recent_approvals,
        brand=brand,
        website=website,
        active_conversation=conversation,
        pending_approvals=pending_approvals,
        pending_approval_count=pending_approval_count,
    )
