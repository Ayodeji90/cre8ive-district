import asyncio
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_role
from app.db import get_db
from app.deps import get_event_bus
from app.events import EventBus
from app.models import User
from app.schemas.common import Page
from app.schemas.review import (
    RejectRequest,
    ReviewCreate,
    ReviewDetail,
    ReviewListItem,
    ReviewResponse,
    RevisionRequest,
)
from app.services import reviews as review_service

admin_router = APIRouter(prefix="/admin", tags=["admin"])
internal_router = APIRouter(prefix="/reviews", tags=["reviews"])


@internal_router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    event_bus: EventBus = Depends(get_event_bus),
    user: User = Depends(require_role("admin", "designer")),
):
    try:
        return await review_service.create_review(db, event_bus=event_bus, **payload.model_dump())
    except review_service.ReviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@admin_router.get("/reviews", response_model=Page[ReviewListItem])
async def list_reviews(
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "designer")),
) -> Page[ReviewListItem]:
    try:
        items, total = await review_service.list_reviews(
            db, status=status_filter, page=page, limit=limit
        )
    except review_service.ReviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Page(
        items=[ReviewListItem.model_validate(item) for item in items],
        total=total,
        page=page,
        limit=limit,
    )


@admin_router.get("/reviews/{review_id}", response_model=ReviewDetail)
async def get_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "designer")),
) -> ReviewDetail:
    try:
        return await review_service.get_review(db, review_id)
    except review_service.ReviewError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@admin_router.post("/reviews/{review_id}/claim", response_model=ReviewResponse)
async def claim_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "designer")),
    event_bus: EventBus = Depends(get_event_bus),
):
    try:
        review = await review_service.claim_review(db, review_id, user.id)
    except review_service.ReviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await event_bus.publish(
        "review_claimed",
        {"review_id": str(review.id), "reviewer": user.name or user.email, "action": "claimed"},
    )
    return review


@admin_router.post("/reviews/{review_id}/approve", response_model=ReviewResponse)
async def approve_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "designer")),
    event_bus: EventBus = Depends(get_event_bus),
):
    try:
        review = await review_service.approve_review(db, review_id, event_bus=event_bus)
    except review_service.ReviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Approval starts the render → delivery chain in the background.
    if review.brand_id is not None:
        from app.services.jobs import enqueue_asset_render

        await enqueue_asset_render(review.brand_id)
    return review


@admin_router.post("/reviews/{review_id}/revise", response_model=ReviewResponse)
async def revise_review(
    review_id: uuid.UUID,
    payload: RevisionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "designer")),
    event_bus: EventBus = Depends(get_event_bus),
):
    try:
        return await review_service.revise_review(
            db, review_id, payload.notes, event_bus=event_bus
        )
    except review_service.ReviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@admin_router.post("/reviews/{review_id}/reject", response_model=ReviewResponse)
async def reject_review(
    review_id: uuid.UUID,
    payload: RejectRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "designer")),
    event_bus: EventBus = Depends(get_event_bus),
):
    try:
        return await review_service.reject_review(
            db, review_id, payload.reason, event_bus=event_bus
        )
    except review_service.ReviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@admin_router.get("/events")
async def admin_events(
    event_bus: EventBus = Depends(get_event_bus),
    user: User = Depends(require_role("admin", "designer")),
) -> StreamingResponse:
    async def stream():
        yield "retry: 5000\n\n"
        iterator = event_bus.subscribe()
        try:
            while True:
                try:
                    event = await asyncio.wait_for(anext(iterator), timeout=15)
                except TimeoutError:
                    yield ": keep-alive\n\n"
                    continue
                yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
        except asyncio.CancelledError:  # pragma: no cover - client disconnect
            raise
        finally:
            await iterator.aclose()

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
