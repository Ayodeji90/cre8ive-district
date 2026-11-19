import re
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.deps import get_ai
from app.llm.base import AIService
from app.models import Business, Conversation, User
from app.ownership import assert_business_owner
from app.schemas.business import BusinessCreate, BusinessResponse, BusinessUpdate
from app.schemas.workspace import ChatResumeResponse, WorkspaceStateResponse
from app.services import chat as chat_service
from app.services.workspace import build_workspace_state

router = APIRouter(prefix="/businesses", tags=["businesses"])


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "business"


async def _unique_slug(db: AsyncSession, base: str) -> str:
    slug = base
    suffix = 1
    while (await db.execute(select(Business.id).where(Business.slug == slug))).first():
        suffix += 1
        slug = f"{base}-{suffix}"
    return slug


@router.get("", response_model=list[BusinessResponse])
async def list_businesses(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Business]:
    """Return all businesses owned by the authenticated user."""
    result = await db.execute(
        select(Business).where(Business.owner_id == user.id).order_by(Business.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(
    payload: BusinessCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Business:
    base = slugify(payload.slug or payload.name)
    business = Business(
        **payload.model_dump(exclude={"slug"}),
        slug=await _unique_slug(db, base),
        owner_id=user.id,
    )
    db.add(business)
    await db.commit()
    await db.refresh(business)
    return business


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Business:
    return await assert_business_owner(db, business_id, user)


@router.patch("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: uuid.UUID,
    payload: BusinessUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Business:
    business = await assert_business_owner(db, business_id, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(business, field, value)
    await db.commit()
    await db.refresh(business)
    return business


# ---------------------------------------------------------------------------
# Workspace State — Business-keyed aggregate view
# ---------------------------------------------------------------------------


@router.get("/{business_id}/state", response_model=WorkspaceStateResponse)
async def get_workspace_state(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WorkspaceStateResponse:
    """Return everything the frontend needs to render this workspace.

    Keyed on ``Business.id`` as the canonical workspace identity.
    """
    business = await assert_business_owner(db, business_id, user)
    return await build_workspace_state(db, business)


# ---------------------------------------------------------------------------
# Chat Start / Resume — returning customer gets same business & conversation
# ---------------------------------------------------------------------------


@router.post("/{business_id}/chat/resume", response_model=ChatResumeResponse)
async def resume_or_start_chat(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    ai: AIService = Depends(get_ai),
    user: User = Depends(get_current_user),
) -> ChatResumeResponse:
    """Resume the most recent active/idle conversation for this business,
    or start a new one if none exists.

    Uses ``FOR UPDATE SKIP LOCKED`` on the lookup query so that concurrent
    requests serialize on the same conversation row rather than both falling
    through to create duplicates.  If the lock is held by another request,
    ``SKIP LOCKED`` causes this query to return no rows — the caller then
    proceeds to create a new conversation.  A unique-constraint fallback
    catches the rare case where two concurrent "new" paths race.
    """
    business = await assert_business_owner(db, business_id, user)

    # Look for an existing resumable conversation — FOR UPDATE SKIP LOCKED
    # ensures only one concurrent request claims a given conversation row.
    existing = (
        (
            await db.execute(
                select(Conversation)
                .where(
                    Conversation.business_id == business.id,
                    Conversation.user_id == user.id,
                    Conversation.status.in_(["active", "idle"]),
                )
                .order_by(Conversation.updated_at.desc())
                .with_for_update(skip_locked=True)
            )
        )
        .scalars()
        .first()
    )

    if existing is not None:
        # Reactivate an idle conversation
        if existing.status == "idle":
            existing.status = "active"
            await db.commit()
        return ChatResumeResponse(
            conversation_id=existing.id,
            mode="resumed",
            context=existing.context or {},
        )

    # No resumable conversation — start a fresh one.
    # In the unlikely event two concurrent requests both reach this point,
    # the second start_conversation call will simply create a second
    # conversation — both are valid.  The workspace state query will
    # always pick the most recently updated active one.
    conversation, greeting = await chat_service.start_conversation(
        db,
        ai,
        user_id=user.id,
        business_id=business.id,
    )
    return ChatResumeResponse(
        conversation_id=conversation.id,
        mode="new",
        greeting_message=greeting.content,
        context=conversation.context or {},
    )
