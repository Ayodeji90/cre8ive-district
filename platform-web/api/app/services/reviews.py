"""Approval queue: listing, claiming and status transitions."""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.events import EventBus
from app.logging import get_logger
from app.models import Brand, Business, Conversation, Message, Order, Review, Website
from app.schemas.brand import WebsiteResponse
from app.schemas.business import BusinessResponse
from app.schemas.order import OrderResponse
from app.schemas.review import ReviewDetail

log = get_logger(__name__)

VALID_STATUSES = {"pending", "in_progress", "approved", "revision_requested", "rejected"}


class ReviewError(RuntimeError):
    pass


async def create_review(
    db: AsyncSession,
    *,
    brand_id: uuid.UUID | None = None,
    order_id: uuid.UUID | None = None,
    website_id: uuid.UUID | None = None,
    event_bus: EventBus | None = None,
) -> Review:
    if not any((brand_id, order_id, website_id)):
        raise ReviewError("A review needs a brand, website or order")
    review = Review(
        brand_id=brand_id, order_id=order_id, website_id=website_id, status="pending"
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    if event_bus is not None:
        await event_bus.publish("new_review", {"review_id": str(review.id), "action": "created"})
    return review


async def list_reviews(
    db: AsyncSession, *, status: str | None = None, page: int = 1, limit: int = 20
) -> tuple[list[dict[str, Any]], int]:
    query = (
        select(Review, Brand, Business)
        .outerjoin(Brand, Review.brand_id == Brand.id)
        .outerjoin(Business, Brand.business_id == Business.id)
    )
    if status:
        if status not in VALID_STATUSES:
            raise ReviewError(f"Unknown review status: {status}")
        query = query.where(Review.status == status)

    total = (
        await db.execute(select(func.count()).select_from(query.subquery()))
    ).scalar_one()
    rows = (
        await db.execute(
            query.order_by(Review.created_at.desc()).offset((page - 1) * limit).limit(limit)
        )
    ).all()

    items = []
    for review, brand, business in rows:
        thumbnail = None
        if brand and brand.logo_urls:
            first = brand.logo_urls[0]
            thumbnail = first.get("url") if isinstance(first, dict) else str(first)
        items.append(
            {
                "id": review.id,
                "brand_id": review.brand_id,
                "order_id": review.order_id,
                "business_id": business.id if business else None,
                "business_name": business.name if business else None,
                "brand_thumbnail": thumbnail,
                "status": review.status,
                "reviewer_id": review.reviewer_id,
                "created_at": review.created_at,
            }
        )
    return items, total


async def get_review(db: AsyncSession, review_id: uuid.UUID) -> ReviewDetail:
    review = (
        await db.execute(
            select(Review)
            .where(Review.id == review_id)
            .options(selectinload(Review.brand), selectinload(Review.order))
        )
    ).scalar_one_or_none()
    if review is None:
        raise ReviewError("Review not found")

    brand_payload = None
    business = None
    conversation_payload = None

    if review.brand is not None:
        brand = review.brand
        brand_payload = {
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
        business = await db.get(Business, brand.business_id)

        conversation = (
            await db.execute(
                select(Conversation)
                .where(Conversation.business_id == brand.business_id)
                .order_by(Conversation.created_at.desc())
            )
        ).scalars().first()
        if conversation is not None:
            messages = (
                await db.execute(
                    select(Message)
                    .where(Message.conversation_id == conversation.id)
                    .order_by(Message.created_at.asc())
                )
            ).scalars().all()
            conversation_payload = {
                "id": str(conversation.id),
                "context": conversation.context,
                "messages": [
                    {
                        "role": message.role,
                        "content": message.content,
                        "created_at": message.created_at.isoformat(),
                    }
                    for message in messages
                ],
            }

    website = None
    if review.website_id:
        website_row = await db.get(Website, review.website_id)
        if website_row is not None:
            website = WebsiteResponse.model_validate(website_row)

    order = await db.get(Order, review.order_id) if review.order_id else None

    return ReviewDetail(
        id=review.id,
        order_id=review.order_id,
        brand_id=review.brand_id,
        website_id=review.website_id,
        reviewer_id=review.reviewer_id,
        status=review.status,
        notes=review.notes,
        reviewed_at=review.reviewed_at,
        created_at=review.created_at,
        updated_at=review.updated_at,
        brand=brand_payload,
        business=BusinessResponse.model_validate(business) if business else None,
        order=OrderResponse.model_validate(order) if order else None,
        website=website,
        conversation=conversation_payload,
    )


async def _load(db: AsyncSession, review_id: uuid.UUID) -> Review:
    review = await db.get(Review, review_id)
    if review is None:
        raise ReviewError("Review not found")
    return review


async def claim_review(
    db: AsyncSession, review_id: uuid.UUID, reviewer_id: uuid.UUID
) -> Review:
    review = await _load(db, review_id)
    if review.status not in {"pending", "in_progress"}:
        raise ReviewError(f"Cannot claim a review in status '{review.status}'")
    review.reviewer_id = reviewer_id
    review.status = "in_progress"
    await db.commit()
    await db.refresh(review)
    return review


async def approve_review(
    db: AsyncSession, review_id: uuid.UUID, *, event_bus: EventBus | None = None
) -> Review:
    review = await _load(db, review_id)
    if review.status == "approved":
        return review
    review.status = "approved"
    review.reviewed_at = datetime.now(UTC)
    if review.brand_id:
        brand = await db.get(Brand, review.brand_id)
        if brand is not None:
            brand.status = "approved"
    await db.commit()
    await db.refresh(review)
    if event_bus is not None:
        await event_bus.publish(
            "review_approved",
            {
                "review_id": str(review.id),
                "brand_id": str(review.brand_id) if review.brand_id else None,
                "action": "approved",
            },
        )
    return review


async def revise_review(
    db: AsyncSession, review_id: uuid.UUID, notes: str, *, event_bus: EventBus | None = None
) -> Review:
    review = await _load(db, review_id)
    review.status = "revision_requested"
    review.notes = notes
    review.reviewed_at = datetime.now(UTC)
    if review.brand_id:
        brand = await db.get(Brand, review.brand_id)
        if brand is not None:
            brand.status = "draft"
    await db.commit()
    await db.refresh(review)
    if event_bus is not None:
        await event_bus.publish(
            "review_revised",
            {"review_id": str(review.id), "notes": notes, "action": "revision_requested"},
        )
    return review


async def reject_review(
    db: AsyncSession, review_id: uuid.UUID, reason: str, *, event_bus: EventBus | None = None
) -> Review:
    review = await _load(db, review_id)
    review.status = "rejected"
    review.notes = reason
    review.reviewed_at = datetime.now(UTC)
    if review.brand_id:
        brand = await db.get(Brand, review.brand_id)
        if brand is not None:
            brand.status = "draft"
    await db.commit()
    await db.refresh(review)
    if event_bus is not None:
        await event_bus.publish(
            "review_rejected",
            {"review_id": str(review.id), "reason": reason, "action": "rejected"},
        )
    return review
