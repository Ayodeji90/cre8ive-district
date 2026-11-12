"""Brand generation orchestrator.

Calls the AI engineer's `AIService` methods in order, persists the result, opens
a review, and notifies the admin dashboard.
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.events import EventBus
from app.llm.base import AIService
from app.logging import get_logger
from app.models import Brand, Business, Review

log = get_logger(__name__)


class BrandGenerationError(RuntimeError):
    pass


async def latest_brand(db: AsyncSession, business_id: uuid.UUID) -> Brand | None:
    result = await db.execute(
        select(Brand).where(Brand.business_id == business_id).order_by(Brand.version.desc())
    )
    return result.scalars().first()


async def generate_brand(
    db: AsyncSession,
    ai: AIService,
    business_id: uuid.UUID,
    *,
    event_bus: EventBus | None = None,
    order_id: uuid.UUID | None = None,
) -> Brand:
    business = await db.get(Business, business_id)
    if business is None:
        raise BrandGenerationError("Business not found")

    description = business.description or business.name
    industry = business.industry or "general"

    log.info("brand_generation_started", business_id=str(business_id))
    strategy = await ai.generate_strategy(description, industry, business.preferences or {})
    logo_urls = await ai.generate_logos(
        strategy, industry, (business.preferences or {}).get("style_keywords")
    )
    palette = await ai.derive_palette(strategy, industry)
    fonts = await ai.select_fonts(strategy)
    copy = await ai.generate_copy(strategy)
    validation = await ai.validate_output(strategy, palette, fonts, logo_urls)

    if not validation.passed:
        log.warning(
            "brand_validation_failed",
            business_id=str(business_id),
            failures=validation.failures,
        )

    previous = await latest_brand(db, business_id)
    version = previous.version + 1 if previous else 1

    brand = Brand(
        business_id=business_id,
        version=version,
        strategy=strategy.model_dump(),
        logo_urls=[
            {"url": url, "size": "1024x1024", "format": url.rsplit(".", 1)[-1]}
            for url in logo_urls
        ],
        colors=palette.model_dump(),
        fonts=fonts.model_dump(),
        copy=copy.model_dump(),
        status="draft",
    )
    db.add(brand)
    await db.commit()
    await db.refresh(brand)

    review = Review(brand_id=brand.id, order_id=order_id, status="pending")
    db.add(review)
    await db.commit()
    await db.refresh(review)

    if event_bus is not None:
        await event_bus.publish(
            "new_review",
            {
                "review_id": str(review.id),
                "brand_id": str(brand.id),
                "business_name": business.name,
                "action": "created",
            },
        )

    log.info(
        "brand_generation_completed",
        business_id=str(business_id),
        brand_id=str(brand.id),
        version=version,
        validation_passed=validation.passed,
    )
    return brand


async def brand_payload(db: AsyncSession, brand: Brand) -> dict[str, Any]:
    return {
        "id": str(brand.id),
        "business_id": str(brand.business_id),
        "version": brand.version,
        "strategy": brand.strategy,
        "logo_urls": brand.logo_urls,
        "colors": brand.colors,
        "fonts": brand.fonts,
        "copy": brand.copy,
        "guidelines_pdf": brand.guidelines_pdf,
        "kit_zip_url": brand.kit_zip_url,
        "status": brand.status,
    }
