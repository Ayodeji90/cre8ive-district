import asyncio
import re
import uuid
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.deps import get_ai
from app.llm.base import AIService
from app.models import Business, Conversation, NewConvSlot, User
from app.ownership import assert_business_owner
from app.schemas.business import BusinessCreate, BusinessResponse, BusinessUpdate
from app.schemas.workspace import ChatResumeResponse, WorkspaceStateResponse
from app.services import chat as chat_service
from app.services.workspace import build_workspace_state


class ChatResumeRequest(BaseModel):
    initial_idea: str | None = None


router = APIRouter(prefix="/businesses", tags=["businesses"])
_chat_resume_locks: dict[tuple[uuid.UUID, uuid.UUID], asyncio.Lock] = {}


def _serialize_chat_resume(handler: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """Serialize same-process resumes; the database slot covers other workers."""

    @wraps(handler)
    async def wrapped(*args: Any, **kwargs: Any) -> Any:
        business_id = kwargs["business_id"]
        user: User = kwargs["user"]
        key = (business_id, user.id)
        lock = _chat_resume_locks.setdefault(key, asyncio.Lock())
        async with lock:
            return await handler(*args, **kwargs)

    return wrapped


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


# ---------------------------------------------------------------------------
# New-conversation claim slot — serializes concurrent "no resumable" paths
# ---------------------------------------------------------------------------


async def _preseed_new_conv_slot(
    db: AsyncSession, business_id: uuid.UUID, owner_id: uuid.UUID, conversation_id: uuid.UUID
) -> None:
    """Persist the conversation that was just created so later losers can pick it
    up without calling start_conversation themselves."""
    await db.execute(
        update(NewConvSlot)
        .where(
            NewConvSlot.business_id == business_id,
            NewConvSlot.owner_id == owner_id,
        )
        .values(conversation_id=conversation_id)
    )
    await db.flush()


# Older function name kept for backwards compatibility with any in-code callers.
_rewind_new_conv_slot = _preseed_new_conv_slot


async def _claim_new_conv_slot(
    db: AsyncSession, business_id: uuid.UUID, owner_id: uuid.UUID
) -> uuid.UUID | None:
    """Atomically claim the new-conversation slot for (business_id, owner_id).

    Uses ``ON CONFLICT DO UPDATE`` so exactly one concurrent claimant sees the
    freshly inserted (still-empty) row as its own and returns ``None``; every
    other concurrent claimant re-reads a conversation_id that was already
    preseeded by the winner and returns that id as "resumed".

    The caller must run inside a transaction.  Any database error is propagated
    to the caller instead of being swallowed.
    """
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    pg_stmt = (
        pg_insert(NewConvSlot)
        .values(business_id=business_id, owner_id=owner_id, conversation_id=None)
        .on_conflict_do_update(
            index_elements=["business_id", "owner_id"],
            set_={
                # touch the row so later readers can use a fresh snapshot; the
                # conversation_id itself is only written by the winner via
                # _preseed_new_conv_slot, never by the claim itself.
                NewConvSlot.business_id: NewConvSlot.business_id
            },
        )
    )
    await db.execute(pg_stmt)

    row = (
        (
            await db.execute(
                select(NewConvSlot.conversation_id).where(
                    NewConvSlot.business_id == business_id,
                    NewConvSlot.owner_id == owner_id,
                )
            )
        )
        .scalars()
        .first()
    )

    # ``select(.NewConvSlot.conversation_id)`` returns the scalar value
    # directly via ``.scalars()``, so ``row`` is already the UUID (or None).
    return row


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

# Chat Resume — returning customer gets same business & conversation
# ---------------------------------------------------------------------------


@router.post("/{business_id}/chat/resume", response_model=ChatResumeResponse)
@_serialize_chat_resume
async def resume_or_start_chat(
    business_id: uuid.UUID,
    payload: ChatResumeRequest | None = Body(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    ai: AIService | None = Depends(get_ai),
) -> ChatResumeResponse:
    """Resume the most recent active/idle conversation for this business,
    or start a new one if none exists.

    Concurrency contract (PostgreSQL):

    1. Find an existing active/idle conversation with FOR UPDATE SKIP LOCKED.
       If one exists, reactivate an idle one and return it as "resumed".

    2. Otherwise atomically claim the per-(business, owner) new-conversation
       slot with ``ON CONFLICT DO UPDATE`` so exactly one concurrent claimant
       wins the right to create. After claiming, re-read for an active/idle
       conversation a second time: a concurrent winner may have created one
       between our first lookup and our claim.

    3. If the slot already carries a preseeded conversation_id (or a
       conversation appeared between steps 1 and 2), return that conversation
       as "resumed" — both concurrent callers end on one conversation id.

    4. Otherwise create a fresh conversation, preseed the slot, and return
       "new".

    Any database error is propagated to the caller; we never swallow it and
    continue on a stale path.
    """
    business = await assert_business_owner(db, business_id, user)

    # --- Step 1: existing resumable conversation ---
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
        if existing.status == "idle":
            existing.status = "active"
            await db.commit()
        return ChatResumeResponse(
            conversation_id=existing.id,
            mode="resumed",
            business_id=business.id,
            context=existing.context or {},
        )

    # --- Step 2: atomically claim the new-conversation slot ---
    claimed = await _claim_new_conv_slot(db, business.id, user.id)

    # --- Step 3: re-read for a conversation that appeared after the claim ---
    # A concurrent winner may have created a conversation between step 1 and
    # step 2, or its preseed may have landed just now. Re-checking here means
    # we never create a second conversation when one already exists.
    recheck = (
        (
            await db.execute(
                select(Conversation)
                .where(
                    Conversation.business_id == business.id,
                    Conversation.user_id == user.id,
                    Conversation.status.in_(["active", "idle"]),
                )
                .order_by(Conversation.updated_at.desc())
            )
        )
        .scalars()
        .first()
    )
    if recheck is not None:
        return ChatResumeResponse(
            conversation_id=recheck.id,
            mode="resumed",
            business_id=business.id,
            context=recheck.context or {},
        )

    if claimed is not None:
        # The slot points at a conversation the winner created. Verify it is
        # still resumable: if it was closed, deleted, or never materialized,
        # clear the slot and create a fresh one instead of returning a stale ID.
        stale_check = (
            (
                await db.execute(
                    select(Conversation).where(
                        Conversation.id == claimed,
                        Conversation.business_id == business.id,
                        Conversation.user_id == user.id,
                        Conversation.status.in_(["active", "idle"]),
                    )
                )
            )
            .scalars()
            .first()
        )
        if stale_check is not None:
            return ChatResumeResponse(
                conversation_id=claimed,
                mode="resumed",
                business_id=business.id,
                context=stale_check.context or {},
            )
        # Slot is stale or the conversation vanished — clear it and fall
        # through to create a new conversation.
        await db.execute(
            update(NewConvSlot)
            .where(
                NewConvSlot.business_id == business.id,
                NewConvSlot.owner_id == user.id,
            )
            .values(conversation_id=None)
        )
        await db.commit()

    # --- Step 4: create a fresh conversation ---
    if ai is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI services are not configured",
        )
    conversation, greeting = await chat_service.start_conversation(
        db,
        ai,
        user_id=user.id,
        business_id=business.id,
        initial_idea=payload.initial_idea if payload else None,
    )
    await _preseed_new_conv_slot(db, business.id, user.id, conversation.id)
    await db.commit()
    await db.refresh(conversation)
    return ChatResumeResponse(
        conversation_id=conversation.id,
        mode="new",
        business_id=business.id,
        greeting=greeting.content,
        context=conversation.context or {},
    )
