import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.deps import get_ai, get_event_bus
from app.events import EventBus
from app.llm.base import AIService
from app.models import Brand, Business, Order, User
from app.schemas.brand import BrandGenerateRequest, BrandResponse
from app.services.brand_gen import BrandGenerationError, generate_brand

router = APIRouter(prefix="/brands", tags=["brands"])


@router.post("/generate", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def generate(
    payload: BrandGenerateRequest,
    db: AsyncSession = Depends(get_db),
    ai: AIService = Depends(get_ai),
    event_bus: EventBus = Depends(get_event_bus),
    user: User = Depends(get_current_user),
) -> Brand:
    business = await db.get(Business, payload.business_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")

    paid_order = (
        await db.execute(
            select(Order).where(
                Order.business_id == payload.business_id, Order.status == "paid"
            )
        )
    ).scalars().first()
    if paid_order is None:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="A paid order is required before generating a brand",
        )

    try:
        brand = await generate_brand(db, ai, payload.business_id, event_bus=event_bus)
    except BrandGenerationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return brand


@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Brand:
    brand = await db.get(Brand, brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.get("/business/{business_id}", response_model=BrandResponse)
async def get_latest_brand(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Brand:
    brand = (
        await db.execute(
            select(Brand)
            .where(Brand.business_id == business_id)
            .order_by(Brand.version.desc())
        )
    ).scalars().first()
    if brand is None:
        raise HTTPException(status_code=404, detail="No brand generated yet")
    return brand
