"""Build the Business-keyed workspace state response.

Collects latest brand, website, active conversation, and pending approval
count into a single response that the frontend fetches on workspace load.
"""

from __future__ import annotations

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging import get_logger
from app.models.brand import Brand
from app.models.business import Business
from app.models.conversation import Conversation
from app.models.project import ApprovalItem, Project
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
    pending_approvals = 0
    project = await db.scalar(select(Project).where(Project.business_id == business.id))
    if project is not None:
        pending_approvals = (
            await db.execute(
                select(func.count())
                .select_from(ApprovalItem)
                .where(
                    ApprovalItem.project_id == project.id,
                    ApprovalItem.status == "pending",
                )
            )
        ).scalar_one()

    return WorkspaceStateResponse(
        business_id=business.id,
        name=business.name,
        slug=business.slug,
        description=business.description,
        industry=business.industry,
        location=business.location,
        contact_phone=business.contact_phone,
        contact_email=business.contact_email,
        plan=business.plan,
        credit_balance=business.credit_balance,
        status=business.status,
        preferences=dict(business.preferences or {}),
        brand=brand,
        website=website,
        conversation=conversation,
        pending_approvals=pending_approvals,
    )
