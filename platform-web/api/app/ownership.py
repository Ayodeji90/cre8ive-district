"""Reusable business-ownership enforcement.

Usage in a router:
    from app.ownership import require_business_owner

    @router.get("/{business_id}")
    async def my_route(
        business: Business = Depends(require_business_owner),
    ) -> ...:
        ...

Or, when business_id comes from elsewhere (e.g. a path param that isn't the
only thing needed), call `assert_business_owner` directly.
"""

import uuid

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.models import Business, Conversation, User


async def assert_business_owner(
    db: AsyncSession,
    business_id: uuid.UUID,
    user: User,
) -> Business:
    """Load a business and verify *user* owns it. Returns the Business or raises 403/404."""
    business = await db.get(Business, business_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    if business.owner_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this business")
    return business


async def require_business_owner(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Business:
    """FastAPI dependency — load a business and verify the caller owns it."""
    return await assert_business_owner(db, business_id, user)


async def assert_conversation_owner(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    user: User,
) -> Conversation:
    """Require both the conversation and its attached business to belong to the caller."""
    conversation = await db.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not own this conversation")
    if conversation.business_id is not None:
        await assert_business_owner(db, conversation.business_id, user)
    return conversation
