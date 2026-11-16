import re
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.models import Business, User
from app.ownership import assert_business_owner
from app.schemas.business import BusinessCreate, BusinessResponse, BusinessUpdate

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
        select(Business)
        .where(Business.owner_id == user.id)
        .order_by(Business.created_at.desc())
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
