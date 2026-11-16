import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.models import Business, User, Website
from app.ownership import assert_business_owner
from app.services import website_gen

router = APIRouter(prefix="/websites", tags=["websites"])


class GenerateWebsiteRequest(BaseModel):
    business_id: uuid.UUID


class WebsiteStatusResponse(BaseModel):
    business_id: uuid.UUID
    status: str
    deployment_url: str | None = None
    custom_domain: str | None = None
    pages: list[dict[str, Any]] = []
    attempt_count: int = 0
    last_attempt_at: datetime | None = None
    last_error: str | None = None
    updated_at: datetime


@router.post("/generate-and-deploy", status_code=status.HTTP_202_ACCEPTED)
async def generate_and_deploy(
    payload: GenerateWebsiteRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    await assert_business_owner(db, payload.business_id, user)

    try:
        result = await website_gen.queue_website_generation(db, payload.business_id)
        return result
    except website_gen.WebsiteGenerationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{business_id}/retry", status_code=status.HTTP_202_ACCEPTED)
async def retry_website_generation(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    await assert_business_owner(db, business_id, user)
    website = await db.scalar(
        select(Website).where(Website.business_id == business_id).order_by(Website.created_at.desc())
    )
    if website is None:
        raise HTTPException(status_code=404, detail="No website job exists for this business")
    if website.status != "failed":
        raise HTTPException(status_code=409, detail="Only a failed website job can be retried")
    try:
        return await website_gen.queue_website_generation(db, business_id)
    except website_gen.WebsiteGenerationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{business_id}/status", response_model=WebsiteStatusResponse)
async def get_website_status(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WebsiteStatusResponse:
    await assert_business_owner(db, business_id, user)
    stmt = (
        select(Website)
        .where(Website.business_id == business_id)
        .order_by(Website.created_at.desc())
    )
    result = await db.execute(stmt)
    website = result.scalars().first()
    if not website:
        raise HTTPException(status_code=404, detail="No website found for this business")

    return WebsiteStatusResponse(
        business_id=website.business_id,
        status=website.status,
        deployment_url=website.deployment_url,
        custom_domain=website.custom_domain,
        pages=website.pages or [],
        attempt_count=website.attempt_count,
        last_attempt_at=website.last_attempt_at,
        last_error=website.last_error,
        updated_at=website.updated_at,
    )
